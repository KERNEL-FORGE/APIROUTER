from django.db import models
import uuid


class API(models.Model):
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=100, unique=True)
    server_file = models.CharField(max_length=500)
    folder_path = models.CharField(max_length=500, blank=True, null=True)
    port = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stopped')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.prefix})"


class APIRoute(models.Model):
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(API, on_delete=models.CASCADE, related_name='routes')
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.method} {self.path}"


class APIRequestLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api = models.ForeignKey(API, on_delete=models.CASCADE, related_name='logs')
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    status_code = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code}"
