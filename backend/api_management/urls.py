from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APIViewSet, UploadAPIView

router = DefaultRouter()
router.register(r'apis', APIViewSet, basename='api')

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', UploadAPIView.as_view(), name='api-upload'),
]
