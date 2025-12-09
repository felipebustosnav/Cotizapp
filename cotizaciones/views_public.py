from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from empresas.models import Empresa
from productos.models import Producto
from .serializers_public import (
    PublicEmpresaSerializer,
    PublicProductoSerializer,
    PublicCotizacionSerializer
)


class PublicEmpresaView(APIView):
    """
    Vista pública para obtener información de empresa y productos.
    No requiere autenticación.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Obtiene información de la empresa y sus productos activos"""
        empresa = get_object_or_404(Empresa, slug_autoatencion=slug, activo=True)
        
        # Serializar empresa
        empresa_serializer = PublicEmpresaSerializer(empresa, context={'request': request})
        
        # Obtener productos activos de la empresa
        productos = Producto.objects.filter(empresa=empresa, activo=True).order_by('nombre')
        productos_serializer = PublicProductoSerializer(productos, many=True)
        
        return Response({
            'empresa': empresa_serializer.data,
            'productos': productos_serializer.data
        })


class PublicCotizacionView(APIView):
    """
    Vista pública para crear cotizaciones sin autenticación.
    Permite a clientes solicitar cotizaciones desde la página de autoatención.
    """
    permission_classes = [AllowAny]
    
    def post(self, request, slug):
        """Crea una cotización pública"""
        empresa = get_object_or_404(Empresa, slug_autoatencion=slug, activo=True)
        
        serializer = PublicCotizacionSerializer(
            data=request.data,
            context={'empresa': empresa, 'request': request}
        )
        
        if serializer.is_valid():
            # Guardar la cotización inicialmente
            cotizacion = serializer.save()
            
            # Verificar configuración de auto-aprobación
            # Solo si es EMAIL y la empresa tiene activado autoaprobar
            if cotizacion.canal_preferencia == 'EMAIL' and empresa.autoaprobar_cotizaciones:
                from .models import Cotizacion
                from django.utils import timezone
                
                cotizacion.estado = Cotizacion.Estado.ENVIADA
                cotizacion.es_decision_automatica = True
                cotizacion.usuario_decision = None # Decisión del sistema
                cotizacion.fecha_decision = timezone.now()
                cotizacion.save()
                
                # Enviar correo asíncrono
                try:
                    from .tasks import enviar_correo_cotizacion
                    enviar_correo_cotizacion.delay(cotizacion.id)
                except Exception as e:
                    print(f"Error al encolar tarea de correo: {e}")
            
            # Caso WhatsApp Público: Siempre queda en Borrador para revisión manual
            # No hacemos nada extra, ya nace como Borrador.
            
            return Response({
                'message': 'Cotización creada exitosamente',
                'numero': cotizacion.numero,
                'total': float(cotizacion.total),
                'cliente': {
                    'nombre': cotizacion.cliente.nombre,
                    'email': cotizacion.cliente.email
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
