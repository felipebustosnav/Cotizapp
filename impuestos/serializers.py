from rest_framework import serializers
from .models import Impuesto


class ImpuestoSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Impuesto.
    """
    empresa = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Impuesto
        fields = ['id', 'nombre', 'porcentaje', 'activo', 'fecha_creacion', 'fecha_actualizacion', 'empresa']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion', 'empresa']


class ImpuestoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de impuestos.
    """
    class Meta:
        model = Impuesto
    class Meta:
        model = Impuesto
        fields = ['id', 'nombre', 'porcentaje', 'activo', 'fecha_actualizacion']
