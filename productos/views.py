from rest_framework import viewsets, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Producto
from .serializers import ProductoSerializer, ProductoListSerializer
from usuarios.permissions import IsAdministrador


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de productos.
    Solo administradores pueden crear, actualizar y eliminar.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'tipo', 'marca']
    search_fields = ['nombre', 'tipo', 'marca']
    ordering_fields = ['nombre', 'precio', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_queryset(self):
        """Filtra productos por empresa del usuario autenticado y solo activos"""
        if self.request.user.is_superuser:
            return Producto.objects.filter(activo=True)
        return Producto.objects.filter(empresa=self.request.user.empresa, activo=True)
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listado"""
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoSerializer
    
    def get_permissions(self):
        """Solo administradores pueden modificar productos"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: marca el producto como inactivo en lugar de eliminarlo.
        Esto permite mantener el historial en cotizaciones.
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(
            {'detail': 'Producto marcado como inactivo correctamente.'},
            status=status.HTTP_200_OK
        )
    
    def create(self, request, *args, **kwargs):
        """Inyecta la empresa antes de la validación del serializer"""
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
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
        """Guarda el producto"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Desactivación lógica en lugar de eliminación"""
        instance.activo = False
        instance.save()
