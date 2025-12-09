from rest_framework import serializers
from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Empresa.
    """
    logo_url = serializers.SerializerMethodField()
    enlace_autoatencion = serializers.SerializerMethodField()
    
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'rut', 'direccion', 'telefono', 'email', 
                  'logo', 'logo_url', 'mensaje_autoatencion', 
                  'mensaje_correo_cotizacion', 'mensaje_whatsapp_cotizacion',
                  'slug_autoatencion', 'enlace_autoatencion', 
                  'autoaprobar_cotizaciones',
                  'activo', 'fecha_creacion']
        read_only_fields = ['id', 'slug_autoatencion', 'fecha_creacion']
    
    def get_logo_url(self, obj):
        """Retorna la URL completa del logo"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None
    
    def get_enlace_autoatencion(self, obj):
        """Retorna el enlace completo para autoatención"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.generar_enlace_autoatencion())
        return obj.generar_enlace_autoatencion()
