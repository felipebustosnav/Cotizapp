from django.contrib import admin
from .models import Impuesto, ProductoImpuesto


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'porcentaje', 'empresa', 'activo', 'fecha_actualizacion']
    list_filter = ['activo', 'empresa']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(ProductoImpuesto)
class ProductoImpuestoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'impuesto', 'orden']
    list_filter = ['producto__empresa']
