from django.db import models
from django.conf import settings
from django.utils import timezone

class SolicitudCambio(models.Model):
    TIPO_CHOICES = [
        ('PRODUCTO', 'Producto'),
        ('COTIZACION', 'Cotización'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
    ]

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_cambio')
    tipo_entidad = models.CharField(max_length=20, choices=TIPO_CHOICES)
    entidad_id = models.IntegerField(help_text="ID del objeto a modificar")
    
    # Guardamos el snapshot completo de la data propuesta (JSON)
    datos_propuestos = models.JSONField(help_text="Datos completos propuestos para la entidad")
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resolutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_resueltas')
    comentario_resolucion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_solicitud']
        verbose_name = "Solicitud de Cambio"
        verbose_name_plural = "Solicitudes de Cambio"

    def __str__(self):
        return f"Solicitud {self.id} - {self.tipo_entidad} #{self.entidad_id} por {self.solicitante}"
