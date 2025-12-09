from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
import uuid


class Cotizacion(models.Model):
    """
    Modelo de Cotizacion con detalles de productos.
    """
    
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        ENVIADA = 'ENVIADA', 'Enviada'
        ACEPTADA = 'ACEPTADA', 'Aceptada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
    
    numero = models.CharField('Número', max_length=20, unique=True, editable=False)
    uuid = models.UUIDField('UUID', default=uuid.uuid4, editable=False, unique=True)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, related_name='cotizaciones', verbose_name='Cliente')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='cotizaciones', verbose_name='Empresa')
    usuario_creador = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, related_name='cotizaciones_creadas', verbose_name='Creado por')
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_vencimiento = models.DateField('Fecha de vencimiento', blank=True, null=True)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=10, choices=Estado.choices, default=Estado.BORRADOR)
    
    class Canal(models.TextChoices):
        EMAIL = 'EMAIL', 'Correo Electrónico'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        
    canal_preferencia = models.CharField('Canal de preferencia', max_length=10, choices=Canal.choices, default=Canal.EMAIL)
    notas = models.TextField('Notas', blank=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['cliente']),
            models.Index(fields=['fecha_creacion']),
        ]
    
    def __str__(self):
        return f"Cotización {self.numero} - {self.cliente.nombre}"
    
    def save(self, *args, **kwargs):
        """Genera número de cotización automáticamente"""
        if not self.numero:
            # Formato: COT-YYYYMMDD-XXXX
            fecha = timezone.now().strftime('%Y%m%d')
            ultimo = Cotizacion.objects.filter(
                numero__startswith=f'COT-{fecha}'
            ).order_by('-numero').first()
            
            if ultimo:
                ultimo_num = int(ultimo.numero.split('-')[-1])
                nuevo_num = ultimo_num + 1
            else:
                nuevo_num = 1
            
            self.numero = f'COT-{fecha}-{nuevo_num:04d}'
        
        # Establecer fecha de vencimiento si no existe (30 días por defecto)
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = (timezone.now() + timedelta(days=30)).date()
        
        super().save(*args, **kwargs)
    
    def calcular_totales(self):
        """Calcula subtotal y total basado en los detalles"""
        detalles = self.detalles.all()
        self.subtotal = sum(detalle.subtotal for detalle in detalles)
        self.total = sum(detalle.subtotal for detalle in detalles)
        self.save()
    
    def generar_pdf(self):
        """Genera el PDF de la cotización"""
        from .utils.pdf_generator import generar_pdf_cotizacion
        return generar_pdf_cotizacion(self)


class DetalleCotizacion(models.Model):
    """
    Detalle de productos en una cotización.
    """
    
    cotizacion = models.ForeignKey(Cotizacion, on_delete=models.CASCADE, related_name='detalles', verbose_name='Cotización')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='detalles_cotizacion', verbose_name='Producto')
    cantidad = models.PositiveIntegerField('Cantidad', validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField('Precio unitario', max_digits=10, decimal_places=2)
    impuesto = models.DecimalField('Impuesto (%)', max_digits=5, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=12, decimal_places=2, editable=False)
    
    class Meta:
        verbose_name = 'Detalle de cotización'
        verbose_name_plural = 'Detalles de cotización'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente"""
        self.subtotal = self.calcular_subtotal()
        super().save(*args, **kwargs)
    
    def calcular_subtotal(self):
        """Calcula el subtotal con impuesto incluido"""
        precio_base = self.precio_unitario * self.cantidad
        impuesto_monto = precio_base * (self.impuesto / Decimal('100'))
        return precio_base + impuesto_monto
