from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioListSerializer
from .permissions import IsAdministrador, IsSameEmpresa

User = get_user_model()


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    Solo administradores pueden crear, actualizar y eliminar usuarios.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsSameEmpresa]
    
    def get_queryset(self):
        """Filtra usuarios por empresa del usuario autenticado"""
        if self.request.user.is_superuser:
            return Usuario.objects.all()
        if self.request.user.empresa:
            return Usuario.objects.filter(empresa=self.request.user.empresa)
        return Usuario.objects.none()
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listado"""
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        """
        Permisos personalizados según la acción.
        Solo administradores pueden crear, actualizar y eliminar.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdministrador()]
        return [permissions.IsAuthenticated(), IsSameEmpresa()]
    
    def perform_create(self, serializer):
        """Asigna la empresa del usuario autenticado al nuevo usuario"""
        if not serializer.validated_data.get('empresa'):
            if self.request.user.empresa:
                serializer.save(empresa=self.request.user.empresa)
            else:
                # Superusuario creando usuario sin empresa asignada
                serializer.save()
        else:
            serializer.save()
    
    def destroy(self, request, *args, **kwargs):
        """Eliminación lógica del usuario"""
        instance = self.get_object()
        instance.activo = False
        instance.save()
        return Response(
            {'message': 'Usuario desactivado correctamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna el perfil del usuario autenticado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
