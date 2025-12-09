from django.db import models
from decimal import Decimal


class Producto(models.Model):
    """
    Modelo de Producto sin manejo de stock, solo activo/inactivo.
    Soporta múltiples impuestos a través de relación ManyToMany.
    """
    nombre = models.CharField('Nombre', max_length=200)
    descripcion = models.TextField('Descripción', blank=True, help_text='Descripción detallada del producto')
    sku = models.CharField('SKU', max_length=50, blank=True, null=True, help_text='Código único del producto')
    tipo = models.CharField('Tipo', max_length=100)
    marca = models.CharField('Marca', max_length=100, blank=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    activo = models.BooleanField('Activo', default=True)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='productos', verbose_name='Empresa')
    
    # Relación ManyToMany con Impuesto a través de ProductoImpuesto
    impuestos = models.ManyToManyField(
        'impuestos.Impuesto',
        through='impuestos.ProductoImpuesto',
        related_name='productos',
        blank=True
    )
    
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['empresa', 'activo']),
            models.Index(fields=['tipo']),
        ]
    
    def __str__(self):
        return f"{self.nombre} - {self.marca}"
    
    def calcular_impuesto_total(self):
        """Calcula el porcentaje total de impuestos activos"""
        total = sum(
            imp.porcentaje 
            for imp in self.impuestos.filter(activo=True)
        )
        return Decimal(str(total))
    
    @property
    def impuesto_total(self):
        """Property para compatibilidad con código existente"""
        return self.calcular_impuesto_total()
    
    def precio_con_impuesto(self):
        """Calcula el precio incluyendo todos los impuestos activos"""
        impuesto_total = self.calcular_impuesto_total()
        return self.precio * (1 + impuesto_total / Decimal('100'))

