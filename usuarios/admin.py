from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'rol', 'empresa', 'activo')
    list_filter = ('rol', 'activo', 'empresa')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('rol', 'empresa', 'activo', 'is_staff', 'is_superuser')}),
        ('Fechas', {'fields': ('last_login', 'fecha_creacion', 'fecha_actualizacion')}),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion', 'last_login')
