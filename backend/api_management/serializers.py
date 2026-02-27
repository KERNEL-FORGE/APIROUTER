from rest_framework import serializers
from .models import API, APIRoute, APIRequestLog


class APIRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRoute
        fields = ['id', 'path', 'method', 'description', 'parameters']


class APISerializer(serializers.ModelSerializer):
    routes = APIRouteSerializer(many=True, read_only=True)

    class Meta:
        model = API
        fields = ['id', 'name', 'prefix', 'server_file', 'folder_path', 'port', 'status', 'routes', 'created_at', 'updated_at']


class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = ['id', 'method', 'path', 'request_data', 'response_data', 'status_code', 'timestamp']
