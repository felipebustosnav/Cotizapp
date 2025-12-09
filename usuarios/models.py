from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con roles y relación a empresa.
    """
    
    class Rol(models.TextChoices):
        ADMINISTRADOR = 'ADMIN', 'Administrador'
        EMPLEADO = 'EMPLEADO', 'Empleado'
    
    email = models.EmailField('Correo electrónico', unique=True)
    rol = models.CharField('Rol', max_length=10, choices=Rol.choices, default=Rol.EMPLEADO)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, related_name='usuarios', verbose_name='Empresa', null=True, blank=True)
    activo = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha de creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha de actualización', auto_now=True)
    
    # Sobrescribir username para usar email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == self.Rol.ADMINISTRADOR
    
    def is_empleado(self):
        """Verifica si el usuario es empleado"""
        return self.rol == self.Rol.EMPLEADO
