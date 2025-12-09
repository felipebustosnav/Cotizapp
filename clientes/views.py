from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Cliente
from .serializers import ClienteSerializer, ClienteListSerializer
from usuarios.permissions import IsAdministrador


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de clientes.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'rut', 'email']
    ordering_fields = ['nombre', 'fecha_registro']
    ordering = ['nombre']
    
    def get_queryset(self):
        """Filtra clientes por empresa del usuario autenticado"""
        if self.request.user.is_superuser:
            return Cliente.objects.all()
        if self.request.user.empresa:
            return Cliente.objects.filter(empresa=self.request.user.empresa)
        return Cliente.objects.none()
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listado"""
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer
    
    def get_permissions(self):
        """Solo administradores pueden eliminar clientes"""
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Inyecta la empresa antes de la validación del serializer"""
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Asignar empresa si no viene en el payload y el usuario tiene una asociada
        if 'empresa' not in data:
            if request.user.empresa:
                data['empresa'] = request.user.empresa.id
            elif request.user.is_superuser:
                raise ValidationError({"empresa": "Superusuario debe especificar la empresa."})
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Guarda el cliente"""
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def cotizaciones(self, request, pk=None):
        """Retorna el historial de cotizaciones del cliente"""
        cliente = self.get_object()
        cotizaciones = cliente.cotizaciones.all()
        from cotizaciones.serializers import CotizacionListSerializer
        serializer = CotizacionListSerializer(cotizaciones, many=True)
        return Response(serializer.data)
