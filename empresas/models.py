from django.db import models
from django.utils.text import slugify
import uuid


class Empresa(models.Model):
    """
    Modelo de Empresa que agrupa usuarios, productos y cotizaciones.
    """
    
    nombre = models.CharField('Nombre', max_length=200)
    rut = models.CharField('RUT', max_length=12, unique=True)
    direccion = models.CharField('Dirección', max_length=300, blank=True)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    email = models.EmailField('Correo electrónico', blank=True)
    logo = models.ImageField('Logo', upload_to='logos/', blank=True, null=True)
    mensaje_autoatencion = models.TextField('Mensaje Autoatención', blank=True, help_text='Mensaje que se mostrará en el portal de autoatención')
    mensaje_correo_cotizacion = models.TextField('Mensaje Correo', blank=True, help_text='Mensaje personalizado para el cuerpo del correo de la cotización')
    mensaje_whatsapp_cotizacion = models.TextField('Mensaje WhatsApp', blank=True, help_text='Mensaje personalizado para el envío por WhatsApp')
    slug_autoatencion = models.SlugField('Slug autoatención', max_length=100, unique=True, blank=True)
    autoaprobar_cotizaciones = models.BooleanField('Auto-aprobar Cotizaciones', default=False, help_text='Aprobar automáticamente cotizaciones recibidas por autoatención')
    mensajeria_automatica_activa = models.BooleanField('Mensajería Automática Activa', default=False, help_text='Habilitar envío automático de ofertas/fidelización')
    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Genera slug único para autoatención si no existe o si cambia el nombre"""
        should_generate = not self.slug_autoatencion

        if self.pk:
            try:
                old_instance = Empresa.objects.get(pk=self.pk)
                if old_instance.nombre != self.nombre:
                    should_generate = True
            except Empresa.DoesNotExist:
                pass

        if should_generate:
            base_slug = slugify(self.nombre)
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            self.slug_autoatencion = unique_slug
            
        super().save(*args, **kwargs)
    
    def generar_enlace_autoatencion(self):
        """Retorna el enlace completo para autoatención"""
        return f"/autoatencion/{self.slug_autoatencion}/"
