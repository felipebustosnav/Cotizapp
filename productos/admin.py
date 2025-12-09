from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'marca', 'precio', 'activo', 'empresa')
    list_filter = ('activo', 'tipo', 'empresa')
    search_fields = ('nombre', 'marca', 'tipo')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información del Producto', {'fields': ('nombre', 'tipo', 'marca')}),
        ('Precio', {'fields': ('precio',)}),
        ('Empresa', {'fields': ('empresa',)}),
        ('Estado', {'fields': ('activo',)}),
        ('Fechas', {'fields': ('fecha_creacion', 'fecha_actualizacion')}),
    )
