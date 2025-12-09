from rest_framework import serializers
from .models import Cotizacion, DetalleCotizacion
from clientes.models import Cliente
from productos.models import Producto


class PublicDetalleCotizacionSerializer(serializers.Serializer):
    """Serializer para detalles de cotización pública"""
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    
    def validate_producto_id(self, value):
        """Valida que el producto exista y esté activo"""
        try:
            producto = Producto.objects.get(id=value, activo=True)
            return value
        except Producto.DoesNotExist:
            raise serializers.ValidationError("Producto no encontrado o inactivo.")


class PublicCotizacionSerializer(serializers.Serializer):
    """Serializer para cotizaciones públicas (sin autenticación)"""
    # Datos del cliente
    cliente_nombre = serializers.CharField(max_length=200)
    cliente_email = serializers.EmailField()
    cliente_telefono = serializers.CharField(max_length=15)
    cliente_rut = serializers.CharField(max_length=12, required=False, allow_blank=True)
    
    # Detalles de la cotización
    # Detalles de la cotización
    detalles = PublicDetalleCotizacionSerializer(many=True)
    notas = serializers.CharField(required=False, allow_blank=True)
    canal_preferencia = serializers.ChoiceField(choices=['EMAIL', 'WHATSAPP'], required=False, default='EMAIL')
    
    def validate_detalles(self, value):
        """Valida que haya al menos un producto"""
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto.")
        return value
    
    def create(self, validated_data):
        """Crea la cotización pública"""
        empresa = self.context['empresa']
        detalles_data = validated_data.pop('detalles')
        
        rut = validated_data.get('cliente_rut', '').strip()
        email = validated_data['cliente_email']
        
        cliente = None
        
        # 1. Buscar por RUT (Prioridad Alta)
        if rut:
            cliente = Cliente.objects.filter(empresa=empresa, rut=rut).first()
            
        # 2. Si no encuentra por RUT, buscar por Email
        if not cliente:
            cliente = Cliente.objects.filter(empresa=empresa, email=email).first()
            
        if cliente:
            # Actualizar cliente existente
            cliente.nombre = validated_data['cliente_nombre']
            cliente.telefono = validated_data['cliente_telefono']
            cliente.email = email
            if rut:
                cliente.rut = rut
            cliente.save()
        else:
            # Crear nuevo cliente
            cliente = Cliente.objects.create(
                empresa=empresa,
                email=email,
                nombre=validated_data['cliente_nombre'],
                telefono=validated_data['cliente_telefono'],
                rut=rut
            )
        
        # Crear cotización
        cotizacion = Cotizacion.objects.create(
            cliente=cliente,
            empresa=empresa,
            usuario_creador=None,
            estado=Cotizacion.Estado.BORRADOR,
            notas=validated_data.get('notas', 'Cotización creada desde autoatención'),
            canal_preferencia=validated_data.get('canal_preferencia', 'EMAIL')
        )
        
        # Crear detalles
        for detalle_data in detalles_data:
            producto = Producto.objects.get(id=detalle_data['producto_id'])
            DetalleCotizacion.objects.create(
                cotizacion=cotizacion,
                producto=producto,
                cantidad=detalle_data['cantidad'],
                precio_unitario=producto.precio,
                impuesto=producto.calcular_impuesto_total()
            )
            
        # Calcular totales finales
        cotizacion.calcular_totales()
        
        return cotizacion


class PublicProductoSerializer(serializers.Serializer):
    """Serializer simplificado de productos para vista pública"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    tipo = serializers.CharField()
    marca = serializers.CharField()
    precio = serializers.DecimalField(max_digits=10, decimal_places=2)
    impuesto = serializers.SerializerMethodField()
    precio_con_impuesto = serializers.SerializerMethodField()
    
    def get_impuesto(self, obj):
        return float(obj.calcular_impuesto_total())
    
    def get_precio_con_impuesto(self, obj):
        """Calcula precio con impuesto"""
        return float(obj.precio * (1 + obj.calcular_impuesto_total() / 100))


class PublicEmpresaSerializer(serializers.Serializer):
    """Serializer de empresa para vista pública"""
    nombre = serializers.CharField()
    telefono = serializers.CharField()
    email = serializers.EmailField()
    direccion = serializers.CharField()
    mensaje_autoatencion = serializers.CharField()
    logo_url = serializers.SerializerMethodField()
    
    def get_logo_url(self, obj):
        """Retorna URL del logo"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
        return None
