from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CotizacionViewSet, ReporteViewSet, ReglaOfertaViewSet
from .views_public import PublicEmpresaView, PublicCotizacionView

router = DefaultRouter()
router.register(r'cotizaciones', CotizacionViewSet)
router.register(r'reportes', ReporteViewSet, basename='reportes')
router.register(r'reglas-oferta', ReglaOfertaViewSet, basename='reglas-oferta')

urlpatterns = [
    path('', include(router.urls)),
    # Rutas públicas (sin autenticación)
    path('autoatencion/<slug:slug>/', PublicEmpresaView.as_view(), name='public-empresa'),
    path('autoatencion/<slug:slug>/cotizar/', PublicCotizacionView.as_view(), name='public-cotizar'),
]
