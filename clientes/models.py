from django.db import models
from django.core.validators import RegexValidator
import re


def validar_rut_chileno(rut):
    """
    Valida formato y dígito verificador de RUT chileno.
    """
    rut = rut.replace('.', '').replace('-', '').upper()
    if len(rut) < 2:
        raise ValueError('RUT inválido')
    
    rut_numeros = rut[:-1]
    dv = rut[-1]
    
    if not rut_numeros.isdigit():
        raise ValueError('RUT debe contener solo números')
    
    # Calcular dígito verificador
    suma = 0
    multiplo = 2
    for r in reversed(rut_numeros):
        suma += int(r) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2
    
    dv_calculado = 11 - (suma % 11)
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    if dv != dv_calculado:
        raise ValueError('Dígito verificador inválido')
    
    return True


class Cliente(models.Model):
    """
    Modelo de Cliente con validación de RUT chileno.
    """
    
    nombre = models.CharField('Nombre', max_length=200)
    rut = models.CharField('RUT', max_length=12)
    telefono = models.CharField('Teléfono', max_length=15, blank=True)
    direccion = models.CharField('Dirección', max_length=300, blank=True)
    email = models.EmailField('Correo electrónico')
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='clientes', verbose_name='Empresa')
    fecha_registro = models.DateTimeField('Fecha de registro', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']
        unique_together = [['rut', 'empresa']]
        indexes = [
            models.Index(fields=['empresa', 'email']),
            models.Index(fields=['rut']),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.rut})"
    
    def clean(self):
        """Valida el RUT antes de guardar"""
        from django.core.exceptions import ValidationError
        try:
            validar_rut_chileno(self.rut)
        except ValueError as e:
            raise ValidationError({'rut': str(e)})
    
    def formatear_rut(self):
        """Retorna el RUT formateado (ej: 12.345.678-9)"""
        if not self.rut:
            return ""
            
        rut = self.rut.replace('.', '').replace('-', '')
        
        if len(rut) < 2:
            return self.rut

        rut_numeros = rut[:-1]
        dv = rut[-1]
        
        # Formatear con puntos
        rut_formateado = ''
        for i, digit in enumerate(reversed(rut_numeros)):
            if i > 0 and i % 3 == 0:
                rut_formateado = '.' + rut_formateado
            rut_formateado = digit + rut_formateado
        
        return f"{rut_formateado}-{dv}"
