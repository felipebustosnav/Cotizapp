from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImpuestoViewSet

router = DefaultRouter()
router.register(r'impuestos', ImpuestoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
