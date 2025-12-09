from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Empresa
from .serializers import EmpresaSerializer
from usuarios.permissions import IsAdministrador


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de empresa.
    Solo administradores pueden modificar la información.
    """
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        """Retorna solo la empresa del usuario autenticado"""
        if self.request.user.is_superuser:
            return Empresa.objects.all()
        if self.request.user.empresa:
            return Empresa.objects.filter(id=self.request.user.empresa.id)
        return Empresa.objects.none()
    
    def get_permissions(self):
        """Solo administradores pueden modificar"""
        if self.action in ['update', 'partial_update', 'create', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def mi_empresa(self, request):
        """Retorna la información de la empresa del usuario autenticado"""
        if not request.user.empresa:
             return Response({'detail': 'Usuario sin empresa asignada'}, status=404)
        serializer = self.get_serializer(request.user.empresa)
        return Response(serializer.data)
