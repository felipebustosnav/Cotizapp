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
        """
        Crea usuario. Si no viene password, genera uno temporal y notifica.
        Asigna empresa del admin si corresponde.
        """
        empresa = self.request.user.empresa
        save_kwargs = {}
        
        # Asignar empresa si es Admin de empresa
        if not serializer.validated_data.get('empresa') and empresa:
            save_kwargs['empresa'] = empresa

        # Verificar si hay password, si no, generar temporal
        password = serializer.validated_data.get('password')
        generated_password = None
        
        if not password:
            from .utils.password_utils import generar_password_temporal
            generated_password = generar_password_temporal()
            save_kwargs['password'] = generated_password
            save_kwargs['cambio_password_obligatorio'] = True
        
        # Guardar usuario
        user = serializer.save(**save_kwargs)
        
        # Enviar correo si se generó password
        if generated_password:
            from .tasks import enviar_credenciales_empleado
            try:
                enviar_credenciales_empleado.delay(user.id, generated_password)
            except Exception as e:
                # Loggear error pero no fallar el request
                print(f"Error enviando correo de credenciales: {e}")
    
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

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Resetea la contraseña de un usuario (empleado) y envía una nueva temporal.
        """
        usuario = self.get_object()
        
        # Generar nueva contraseña temporal
        from .utils.password_utils import generar_password_temporal
        password_temporal = generar_password_temporal()
        
        # Actualizar usuario
        usuario.set_password(password_temporal)
        usuario.cambio_password_obligatorio = True
        usuario.save()
        
        # Enviar correo
        from .tasks import enviar_credenciales_empleado
        try:
            enviar_credenciales_empleado.delay(usuario.id, password_temporal)
        except Exception as e:
            return Response(
                {'error': f'Contraseña reseteada pero falló el envío del correo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(
            {'message': 'Contraseña reseteada exitosamente. Se ha enviado un correo al usuario.'},
            status=status.HTTP_200_OK
        )
