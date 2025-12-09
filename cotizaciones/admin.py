from django.contrib import admin
from .models import Cotizacion, DetalleCotizacion


class DetalleCotizacionInline(admin.TabularInline):
    model = DetalleCotizacion
    extra = 1
    readonly_fields = ('subtotal',)


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'empresa', 'estado', 'total', 'fecha_creacion')
    list_filter = ('estado', 'empresa', 'fecha_creacion')
    search_fields = ('numero', 'cliente__nombre', 'cliente__rut')
    readonly_fields = ('numero', 'subtotal', 'total', 'fecha_creacion', 'fecha_actualizacion')
    inlines = [DetalleCotizacionInline]
    
    fieldsets = (
        ('Información Básica', {'fields': ('numero', 'cliente', 'empresa', 'usuario_creador')}),
        ('Fechas', {'fields': ('fecha_creacion', 'fecha_vencimiento', 'fecha_actualizacion')}),
        ('Totales', {'fields': ('subtotal', 'total')}),
        ('Estado', {'fields': ('estado', 'notas')}),
    )


@admin.register(DetalleCotizacion)
class DetalleCotizacionAdmin(admin.ModelAdmin):
    list_display = ('cotizacion', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('cotizacion__empresa',)
    search_fields = ('cotizacion__numero', 'producto__nombre')
    readonly_fields = ('subtotal',)
