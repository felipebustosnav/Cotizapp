from django.contrib import admin
from .models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # If editing an existing object
            form.base_fields['nombre'].help_text = (
                '<div style="color: red; font-weight: bold; background: #ffe6e6; padding: 10px; border: 1px solid red; border-radius: 4px;">'
                '⚠️ ADVERTENCIA: Al cambiar el nombre de la empresa, se generará un nuevo enlace de autoatención. '
                'El enlace antiguo dejará de funcionar inmediatamente. Asegúrese de actualizarlo en todas partes.'
                '</div>'
            )
        return form

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
