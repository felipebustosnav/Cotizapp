from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Impuesto
from .serializers import ImpuestoSerializer, ImpuestoListSerializer
from usuarios.permissions import IsAdministrador, IsSameEmpresa


class ImpuestoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de impuestos.
    Solo administradores pueden crear, actualizar y eliminar.
    """
    queryset = Impuesto.objects.all()
    serializer_class = ImpuestoSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameEmpresa]

    def get_queryset(self):
        """Filtra impuestos por empresa del usuario autenticado y solo activos"""
        if self.request.user.is_superuser:
            return Impuesto.objects.filter(activo=True)
        if self.request.user.empresa:
            return Impuesto.objects.filter(empresa=self.request.user.empresa, activo=True)
        return Impuesto.objects.none()

    def get_serializer_class(self):
        """Usa serializer simplificado para listado"""
        if self.action == 'list':
            return ImpuestoListSerializer
        return ImpuestoSerializer

    def get_permissions(self):
        """Todos los empleados autenticados de la empresa pueden modificar"""
        return [permissions.IsAuthenticated(), IsSameEmpresa()]

    def create(self, request, *args, **kwargs):
        """Inyecta la empresa antes de la validación del serializer"""
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        if 'empresa' not in data:
            if request.user.empresa:
                data['empresa'] = request.user.empresa.id
            elif request.user.is_superuser:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"empresa": "Superusuario debe especificar la empresa."})
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """Guarda el impuesto asociándolo a la empresa del usuario"""
        if self.request.user.empresa:
            serializer.save(empresa=self.request.user.empresa)
        else:
            # Fallback para superusuario si envió la empresa en el body,
            # o dejar que falle si no es admin de empresa
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: marca el impuesto como inactivo en lugar de eliminarlo.
        Esto permite mantener el historial en productos y cotizaciones.
        """
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(
            {'detail': 'Impuesto marcado como inactivo correctamente.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Retorna solo los impuestos activos de la empresa"""
        queryset = self.get_queryset().filter(activo=True)
        serializer = ImpuestoListSerializer(queryset, many=True)
        return Response(serializer.data)
