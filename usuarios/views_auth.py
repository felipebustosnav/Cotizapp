from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.contrib.auth import get_user_model
from empresas.models import Empresa

User = get_user_model()

class RegisterCompanyView(APIView):
    """
    Vista pública para registrar una nueva empresa y su usuario administrador.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Validaciones básicas
        required_fields = ['empresa_nombre', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'detail': f'El campo {field} es obligatorio.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        email = data.get('email')
        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'Este correo electrónico ya está registrado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            with transaction.atomic():
                # 1. Crear Empresa
                empresa = Empresa.objects.create(
                    nombre=data.get('empresa_nombre'),
                    email=email, # Usar mismo email de contacto
                    rut=data.get('rut', ''), # Opcional en registro rápido, idealmente validar
                    telefono=data.get('telefono', '')
                )
                
                # 2. Crear Usuario Admin
                user = User.objects.create_user(
                    email=email,
                    username=email, # Usamos email como username
                    password=data.get('password'),
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    empresa=empresa,
                    rol=User.Rol.ADMINISTRADOR
                )
                
                return Response({
                    'message': 'Empresa registrada exitosamente.',
                    'empresa': {
                        'id': empresa.id,
                        'nombre': empresa.nombre
                    },
                    'usuario': {
                        'id': user.id,
                        'email': user.email
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'detail': f'Error al registrar empresa: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
