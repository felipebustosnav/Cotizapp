from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Impuesto(models.Model):
    """
    Modelo para gestionar impuestos predefinidos por empresa.
    """
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        related_name='impuestos',
        verbose_name='Empresa'
    )
    nombre = models.CharField('Nombre', max_length=100)
    porcentaje = models.DecimalField(
        'Porcentaje',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Porcentaje del impuesto (ej: 19.00 para 19%)'
    )
    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Última actualización', auto_now=True)

    class Meta:
        verbose_name = 'Impuesto'
        verbose_name_plural = 'Impuestos'
        unique_together = ['empresa', 'nombre']
        ordering = ['empresa', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"


class ProductoImpuesto(models.Model):
    """
    Tabla intermedia para relación Many-to-Many entre Producto e Impuesto.
    Permite mantener el orden de aplicación de impuestos.
    """
    producto = models.ForeignKey(
        'productos.Producto',  # String reference to avoid circular import
        on_delete=models.CASCADE,
        related_name='producto_impuestos'
    )
    impuesto = models.ForeignKey(
        Impuesto,
        on_delete=models.CASCADE,
        related_name='producto_impuestos'
    )
    orden = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Producto-Impuesto'
        verbose_name_plural = 'Productos-Impuestos'
        unique_together = ['producto', 'impuesto']
        ordering = ['producto', 'orden']

    def __str__(self):
        return f"{self.producto.nombre} - {self.impuesto.nombre}"
