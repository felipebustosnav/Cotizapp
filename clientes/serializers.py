from rest_framework import serializers
from .models import Cliente, validar_rut_chileno
from django.core.exceptions import ValidationError as DjangoValidationError


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cliente.
    """
    rut_formateado = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'rut', 'rut_formateado', 'telefono', 'email', 'direccion',
                  'empresa', 'empresa_nombre', 'fecha_registro']
        read_only_fields = ['id', 'fecha_registro']
        extra_kwargs = {
            'empresa': {'required': False}
        }
    
    def get_rut_formateado(self, obj):
        """Retorna el RUT formateado"""
        return obj.formatear_rut()
    
    def validate_rut(self, value):
        """Valida el RUT chileno"""
        try:
            validar_rut_chileno(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate_email(self, value):
        """Valida que el email sea único por empresa"""
        # La empresa se asignará automáticamente en el view
        instance_id = self.instance.id if self.instance else None
        
        # Si estamos actualizando, verificar que no exista otro con el mismo email en la misma empresa
        if self.instance and self.instance.empresa:
            if Cliente.objects.filter(email=value, empresa=self.instance.empresa).exclude(id=instance_id).exists():
                raise serializers.ValidationError("Ya existe un cliente con este email en la empresa.")
        return value


class ClienteListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de clientes.
    """
    rut_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'rut', 'rut_formateado', 'email', 'telefono', 'direccion', 'fecha_registro']
    
    def get_rut_formateado(self, obj):
        return obj.formatear_rut()
