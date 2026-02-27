import os
import re
import subprocess
import signal
import json
import tempfile
import shutil
from pathlib import Path
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .models import API, APIRoute, APIRequestLog
from .serializers import APISerializer, APIRouteSerializer, APIRequestLogSerializer


class APIViewSet(viewsets.ModelViewSet):
    queryset = API.objects.all()
    serializer_class = APISerializer

    def _find_available_port(self, start=8001):
        import socket
        for port in range(start, start + 100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', port))
                sock.close()
                return port
            except:
                continue
        return start

    def _parse_server_js(self, file_path):
        routes = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            route_pattern = r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
            matches = re.finditer(route_pattern, content, re.IGNORECASE)
            
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)
                routes.append({
                    'path': path,
                    'method': method,
                    'description': '',
                    'parameters': []
                })
        except Exception as e:
            print(f"Error parsing server.js: {e}")
        
        return routes

    def _start_node_process(self, api_instance):
        if not api_instance.server_file or not os.path.exists(api_instance.server_file):
            return False
        
        work_dir = api_instance.folder_path or os.path.dirname(api_instance.server_file)
        
        try:
            env = os.environ.copy()
            env['PORT'] = str(api_instance.port)
            
            process = subprocess.Popen(
                ['node', api_instance.server_file],
                cwd=work_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            api_instance.status = 'running'
            api_instance.save()
            return True
        except Exception as e:
            api_instance.status = 'error'
            api_instance.save()
            return False

    def _stop_node_process(self, api_instance):
        try:
            for proc in subprocess.os.popen(f"lsof -t -i:{api_instance.port}").readlines():
                os.kill(int(proc.strip()), signal.SIGTERM)
            
            api_instance.status = 'stopped'
            api_instance.save()
            return True
        except:
            api_instance.status = 'stopped'
            api_instance.save()
            return False

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        port = self._find_available_port()
        api = serializer.save(port=port)
        
        routes = self._parse_server_js(api.server_file)
        for route_data in routes:
            APIRoute.objects.create(api=api, **route_data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self._stop_node_process(instance)
        
        if instance.server_file and os.path.exists(instance.server_file):
            try:
                os.remove(instance.server_file)
            except:
                pass
        
        if instance.folder_path and os.path.exists(instance.folder_path):
            try:
                shutil.rmtree(instance.folder_path)
            except:
                pass
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        api = self.get_object()
        success = self._start_node_process(api)
        return Response({'status': 'running' if success else 'error'})

    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        api = self.get_object()
        self._stop_node_process(api)
        return Response({'status': 'stopped'})

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        api = self.get_object()
        logs = api.logs.order_by('-timestamp')[:100]
        serializer = APIRequestLogSerializer(logs, many=True)
        return Response(serializer.data)


class UploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        name = request.data.get('name', 'Untitled API')
        prefix = request.data.get('prefix', 'api')
        server_file = request.FILES.get('server_file')
        folder = request.FILES.get('folder')
        
        if not server_file:
            return Response({'error': 'No server file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        api_dir = Path(settings.API_UPLOAD_DIR)
        api_dir.mkdir(exist_ok=True)
        
        api_folder = api_dir / prefix
        api_folder.mkdir(exist_ok=True)
        
        server_path = api_folder / 'server.js'
        with open(server_path, 'wb+') as f:
            for chunk in server_file.chunks():
                f.write(chunk)
        
        folder_path = None
        if folder:
            folder_path = str(api_folder / 'folder')
            Path(folder_path).mkdir(exist_ok=True)
            for chunk in folder.chunks():
                with open(folder_path + '/data.zip', 'wb+') as f:
                    f.write(chunk)
        
        port = 8001
        import socket
        for p in range(8001, 8100):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', p))
                sock.close()
                port = p
                break
            except:
                continue
        
        api = API.objects.create(
            name=name,
            prefix=prefix,
            server_file=str(server_path),
            folder_path=folder_path,
            port=port,
            status='stopped'
        )
        
        routes = []
        try:
            with open(server_path, 'r') as f:
                content = f.read()
            route_pattern = r"(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]"
            for match in re.finditer(route_pattern, content, re.IGNORECASE):
                routes.append(APIRoute(
                    api=api,
                    method=match.group(1).upper(),
                    path=match.group(2)
                ))
            APIRoute.objects.bulk_create(routes)
        except:
            pass
        
        serializer = APISerializer(api)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProxyView(APIView):
    def proxy(self, request, prefix, path):
        try:
            api = API.objects.get(prefix=prefix, status='running')
        except API.DoesNotExist:
            return Response({'error': 'API not found or not running'}, status=status.HTTP_404_NOT_FOUND)
        
        import requests
        target_url = f"http://localhost:{api.port}/{path}"
        
        try:
            response = requests.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']},
                data=request.data,
                params=request.query_params
            )
            
            return Response(
                response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                status=response.status_code
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_502_BAD_GATEWAY)
