from rest_framework import serializers
from .models import Usuario
from django.contrib.auth.password_validation import validate_password


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    """
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    empresa_slug = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'rol', 
                  'empresa', 'empresa_slug', 'activo', 'password', 'confirm_password', 'fecha_creacion', 'cambio_password_obligatorio']
        read_only_fields = ['id', 'fecha_creacion', 'cambio_password_obligatorio', 'username']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_empresa_slug(self, obj):
        return obj.empresa.slug_autoatencion if obj.empresa else None
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan"""
        if 'password' in attrs and 'confirm_password' in attrs:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        """Crea un nuevo usuario con contraseña hasheada y username = email"""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        
        # Copiar email a username si no viene (aunque es readonly, así que no vendrá)
        if 'email' in validated_data:
            validated_data['username'] = validated_data['email']
            
        usuario = Usuario.objects.create_user(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario
    
    def update(self, instance, validated_data):
        """Actualiza un usuario, hasheando la contraseña si se proporciona"""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de usuarios.
    """
    empresa_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'first_name', 'last_name', 'rol', 'empresa_nombre', 'activo', 'fecha_creacion']

    def get_empresa_nombre(self, obj):
        return obj.empresa.nombre if obj.empresa else None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Las nuevas contraseñas no coinciden."})
        return attrs
