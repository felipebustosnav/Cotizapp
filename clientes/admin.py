from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rut', 'email', 'telefono', 'empresa', 'fecha_registro')
    list_filter = ('empresa', 'fecha_registro')
    search_fields = ('nombre', 'rut', 'email')
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información del Cliente', {'fields': ('nombre', 'rut')}),
        ('Contacto', {'fields': ('email', 'telefono')}),
        ('Empresa', {'fields': ('empresa',)}),
        ('Fechas', {'fields': ('fecha_registro', 'fecha_actualizacion')}),
    )
