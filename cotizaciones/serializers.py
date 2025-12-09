from rest_framework import serializers
from .models import Cotizacion, DetalleCotizacion, ReglaOfertaAutomatica
from productos.serializers import ProductoListSerializer
from clientes.serializers import ClienteListSerializer


class ReglaOfertaAutomaticaSerializer(serializers.ModelSerializer):
    """
    Serializer para ReglaOfertaAutomatica.
    """
    class Meta:
        model = ReglaOfertaAutomatica
        fields = ['id', 'orden', 'tiempo_espera_valor', 'tiempo_espera_unidad', 
                  'descuento_porcentaje', 'tiempo_validez_valor', 'tiempo_validez_unidad']
        read_only_fields = ['id']


class DetalleCotizacionSerializer(serializers.ModelSerializer):
    """
    Serializer para DetalleCotizacion.
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_info = ProductoListSerializer(source='producto', read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, source='subtotal', read_only=True)
    
    class Meta:
        model = DetalleCotizacion
        fields = ['id', 'producto', 'producto_nombre', 'producto_info', 
                  'cantidad', 'precio_unitario', 'impuesto', 'subtotal', 'total']
        read_only_fields = ['id', 'subtotal', 'total']
    
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
    
    usuario_decision_nombre = serializers.CharField(source='usuario_decision.get_full_name', read_only=True)
    
    impuesto = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='subtotal') # Alias for subtotal model field which is gross, waiting override
    subtotal = serializers.SerializerMethodField()
    impuesto = serializers.SerializerMethodField()
    
    class Meta:
        model = Cotizacion
        fields = ['id', 'numero', 'cliente', 'cliente_info', 'empresa', 
                  'usuario_creador', 'usuario_creador_nombre', 'fecha_creacion', 
                  'fecha_vencimiento', 'subtotal', 'impuesto', 'total', 'estado', 'notas', 
                  'canal_preferencia', 'detalles',
                  'usuario_decision', 'usuario_decision_nombre', 'fecha_decision', 'es_decision_automatica', 'motivo_rechazo']
        read_only_fields = ['id', 'numero', 'total', 'fecha_creacion', 
                            'usuario_decision', 'fecha_decision', 'es_decision_automatica']
        extra_kwargs = {
            'empresa': {'required': False},
            'usuario_creador': {'required': False}
        }
    
    def get_subtotal(self, obj):
        """Calcula el subtotal neto (sin impuestos)"""
        return sum(d.cantidad * d.precio_unitario for d in obj.detalles.all())

    def get_impuesto(self, obj):
        """Calcula el monto total de impuestos"""
        # subtotal model field is actually Gross Total (Line Total with Tax)
        # We calculate Tax = Gross Total - Net Total
        # Or Sum(Line Tax Amount)
        
        neto_total = sum(d.cantidad * d.precio_unitario for d in obj.detalles.all())
        gross_total = obj.total # or sum(d.subtotal for d in obj.detalles.all())
        
        # Calculate manually to be precise per line
        tax_total = 0
        for d in obj.detalles.all():
             base = d.cantidad * d.precio_unitario
             tax_amount = base * (d.impuesto / 100)
             tax_total += tax_amount
        return tax_total
    
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
