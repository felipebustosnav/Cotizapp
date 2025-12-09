from rest_framework import serializers
from .models import Producto
from impuestos.serializers import ImpuestoListSerializer
from impuestos.models import ProductoImpuesto
from decimal import Decimal


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto con soporte para múltiples impuestos.
    """
    precio_con_impuesto = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    impuestos = ImpuestoListSerializer(many=True, read_only=True)
    impuestos_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    impuesto_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['id', 'sku', 'nombre', 'descripcion', 'tipo', 'marca', 'precio', 'impuestos', 'impuestos_ids',
                  'impuesto_total', 'precio_con_impuesto', 'activo', 'empresa', 'empresa_nombre', 
                  'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']
        extra_kwargs = {
            'empresa': {'required': False}
        }
    
    def get_precio_con_impuesto(self, obj):
        """Retorna el precio con impuesto incluido"""
        return float(obj.precio_con_impuesto())
    
    def get_impuesto_total(self, obj):
        """Retorna el porcentaje total de impuestos"""
        return float(obj.calcular_impuesto_total())
    
    def validate_precio(self, value):
        """Valida que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value
    
    def create(self, validated_data):
        """Crea producto y asigna impuestos"""
        impuestos_ids = validated_data.pop('impuestos_ids', [])
        producto = Producto.objects.create(**validated_data)
        
        # Asignar impuestos
        for orden, impuesto_id in enumerate(impuestos_ids):
            ProductoImpuesto.objects.create(
                producto=producto,
                impuesto_id=impuesto_id,
                orden=orden
            )
        
        return producto
    
    def update(self, instance, validated_data):
        """Actualiza producto y sus impuestos"""
        impuestos_ids = validated_data.pop('impuestos_ids', None)
        
        # Actualizar campos del producto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si se proporcionan impuestos, reemplazarlos
        if impuestos_ids is not None:
            instance.producto_impuestos.all().delete()
            for orden, impuesto_id in enumerate(impuestos_ids):
                ProductoImpuesto.objects.create(
                    producto=instance,
                    impuesto_id=impuesto_id,
                    orden=orden
                )
        
        return instance


class ProductoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de productos.
    """
    precio_con_impuesto = serializers.SerializerMethodField()
    impuesto_total = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['id', 'sku', 'nombre', 'tipo', 'marca', 'precio', 'impuesto_total', 'precio_con_impuesto', 'activo']
    
    def get_precio_con_impuesto(self, obj):
        return float(obj.precio_con_impuesto())
    
    def get_impuesto_total(self, obj):
        return float(obj.calcular_impuesto_total())

