from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudCambioViewSet

router = DefaultRouter()
router.register(r'solicitudes', SolicitudCambioViewSet, basename='solicitudes')

urlpatterns = [
    path('', include(router.urls)),
]
