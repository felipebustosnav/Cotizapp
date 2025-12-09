from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SolicitudCambio
from .serializers import SolicitudCambioSerializer

class SolicitudCambioViewSet(viewsets.ModelViewSet):
    queryset = SolicitudCambio.objects.all()
    serializer_class = SolicitudCambioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.rol == 'ADMIN':
            return SolicitudCambio.objects.all()
        # Empleados solo ven sus solicitudes
        return SolicitudCambio.objects.filter(solicitante=user)

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """
        Aprueba la solicitud y aplica los cambios a la entidad real.
        Solo ADMIN.
        """
        if request.user.rol != 'ADMIN' and not request.user.is_superuser:
            return Response({'error': 'No tienes permisos para aprobar solicitudes.'}, status=status.HTTP_403_FORBIDDEN)

        solicitud = self.get_object()
        if solicitud.estado != 'PENDIENTE':
            return Response({'error': 'Esta solicitud ya fué procesada.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Lógica dinámica según el tipo
            if solicitud.tipo_entidad == 'PRODUCTO':
                from productos.models import Producto
                from productos.serializers import ProductoSerializer
                
                instance = Producto.objects.get(pk=solicitud.entidad_id)
                serializer = ProductoSerializer(instance, data=solicitud.datos_propuestos, partial=True)
                
            elif solicitud.tipo_entidad == 'COTIZACION':
                from cotizaciones.models import Cotizacion
                from cotizaciones.serializers import CotizacionSerializer
                
                instance = Cotizacion.objects.get(pk=solicitud.entidad_id)
                # CotizacionSerializer.update maneja el update anidado de detalles (borra y crea)
                serializer = CotizacionSerializer(instance, data=solicitud.datos_propuestos, partial=True)
            
            else:
                return Response({'error': 'Tipo de entidad no soportado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validar y Guardar
            if serializer.is_valid():
                serializer.save()
                
                # Actualizar estado de la solicitud
                solicitud.estado = 'APROBADA'
                solicitud.resolutor = request.user
                solicitud.fecha_resolucion = timezone.now()
                solicitud.save()
                
                return Response({'message': 'Solicitud aprobada y cambios aplicados correctamente.'})
            else:
                return Response({'error': 'Datos propuestos inválidos para la entidad.', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': f'Error al aplicar cambios: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def rechazar(self, request, pk=None):
        """
        Rechaza la solicitud.
        Solo ADMIN.
        """
        if request.user.rol != 'ADMIN' and not request.user.is_superuser:
            return Response({'error': 'No tienes permisos para rechazar solicitudes.'}, status=status.HTTP_403_FORBIDDEN)

        solicitud = self.get_object()
        if solicitud.estado != 'PENDIENTE':
            return Response({'error': 'Esta solicitud ya fué procesada.'}, status=status.HTTP_400_BAD_REQUEST)

        motivo = request.data.get('motivo', '')
        
        solicitud.estado = 'RECHAZADA'
        solicitud.resolutor = request.user
        solicitud.fecha_resolucion = timezone.now()
        solicitud.comentario_resolucion = motivo
        solicitud.save()

        return Response({'message': 'Solicitud rechazada.'})
