from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'email', 'telefono', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'rut', 'email')
    readonly_fields = ('slug_autoatencion', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {'fields': ('nombre', 'rut', 'email', 'telefono')}),
        ('Ubicación', {'fields': ('direccion',)}),
        ('Imagen', {'fields': ('logo',)}),
        ('Autoatención', {'fields': ('slug_autoatencion',)}),
        ('Estado', {'fields': ('activo',)}),
        ('Fechas', {'fields': ('fecha_creacion', 'fecha_actualizacion')}),
    )
