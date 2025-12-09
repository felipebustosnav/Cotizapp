from rest_framework import serializers
from .models import Cotizacion, DetalleCotizacion
from productos.serializers import ProductoListSerializer
from clientes.serializers import ClienteListSerializer


class DetalleCotizacionSerializer(serializers.ModelSerializer):
    """
    Serializer para DetalleCotizacion.
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_info = ProductoListSerializer(source='producto', read_only=True)
    
    class Meta:
        model = DetalleCotizacion
        fields = ['id', 'producto', 'producto_nombre', 'producto_info', 
                  'cantidad', 'precio_unitario', 'impuesto', 'subtotal']
        read_only_fields = ['id', 'subtotal']
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")
        return value


class CotizacionSerializer(serializers.ModelSerializer):
    """
    Serializer para Cotizacion con detalles anidados.
    """
    detalles = DetalleCotizacionSerializer(many=True, required=False)
    cliente_info = ClienteListSerializer(source='cliente', read_only=True)
    usuario_creador_nombre = serializers.CharField(source='usuario_creador.get_full_name', read_only=True)
    
    class Meta:
        model = Cotizacion
        fields = ['id', 'numero', 'cliente', 'cliente_info', 'empresa', 
                  'usuario_creador', 'usuario_creador_nombre', 'fecha_creacion', 
                  'fecha_vencimiento', 'subtotal', 'total', 'estado', 'notas', 
                  'canal_preferencia', 'detalles']
        read_only_fields = ['id', 'numero', 'subtotal', 'total', 'fecha_creacion']
        extra_kwargs = {
            'empresa': {'required': False},
            'usuario_creador': {'required': False}
        }
    
    def create(self, validated_data):
        """Crea una cotización con sus detalles"""
        detalles_data = validated_data.pop('detalles', [])
        cotizacion = Cotizacion.objects.create(**validated_data)
        
        for detalle_data in detalles_data:
            DetalleCotizacion.objects.create(cotizacion=cotizacion, **detalle_data)
        
        cotizacion.calcular_totales()
        return cotizacion
    
    def update(self, instance, validated_data):
        """Actualiza una cotización y sus detalles"""
        detalles_data = validated_data.pop('detalles', None)
        
        # Actualizar campos de la cotización
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Si se proporcionan detalles, reemplazarlos
        if detalles_data is not None:
            instance.detalles.all().delete()
            for detalle_data in detalles_data:
                DetalleCotizacion.objects.create(cotizacion=instance, **detalle_data)
            instance.calcular_totales()
        
        return instance


class CotizacionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de cotizaciones.
    """
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_info = ClienteListSerializer(source='cliente', read_only=True)
    
    class Meta:
        model = Cotizacion
        fields = ['id', 'numero', 'cliente_nombre', 'cliente_info', 'fecha_creacion', 'total', 'estado', 'canal_preferencia']
