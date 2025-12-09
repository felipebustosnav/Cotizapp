"""
Script para limpiar datos de prueba y poblar con datos iniciales
incluyendo impuestos predefinidos.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from django.db import transaction
from empresas.models import Empresa
from usuarios.models import Usuario
from impuestos.models import Impuesto
from productos.models import Producto
from clientes.models import Cliente
from cotizaciones.models import Cotizacion, DetalleCotizacion

print("=" * 60)
print("LIMPIEZA Y POBLACIÓN DE DATOS")
print("=" * 60)

with transaction.atomic():
    # 1. Limpiar datos de prueba (manteniendo usuarios y empresas)
    print("\n1. Limpiando datos de prueba...")
    DetalleCotizacion.objects.all().delete()
    print("   ✓ Detalles de cotizaciones eliminados")
    
    Cotizacion.objects.all().delete()
    print("   ✓ Cotizaciones eliminadas")
    
    Producto.objects.all().delete()
    print("   ✓ Productos eliminados")
    
    Cliente.objects.all().delete()
    print("   ✓ Clientes eliminados")
    
    Impuesto.objects.all().delete()
    print("   ✓ Impuestos eliminados")
    
    # 2. Crear impuestos predefinidos para cada empresa
    print("\n2. Creando impuestos predefinidos...")
    empresas = Empresa.objects.all()
    
    for empresa in empresas:
        # IVA (19%)
        iva = Impuesto.objects.create(
            empresa=empresa,
            nombre="IVA",
            porcentaje=19.00,
            activo=True
        )
        print(f"   ✓ IVA creado para {empresa.nombre}")
        
        # Impuesto Específico (ejemplo)
        imp_esp = Impuesto.objects.create(
            empresa=empresa,
            nombre="Impuesto Específico",
            porcentaje=5.00,
            activo=True
        )
        print(f"   ✓ Impuesto Específico creado para {empresa.nombre}")
    
    # 3. Crear productos de ejemplo con impuestos
    print("\n3. Creando productos de ejemplo...")
    for empresa in empresas:
        iva_empresa = Impuesto.objects.get(empresa=empresa, nombre="IVA")
        imp_esp_empresa = Impuesto.objects.get(empresa=empresa, nombre="Impuesto Específico")
        
        # Producto 1: Solo IVA
        prod1 = Producto.objects.create(
            empresa=empresa,
            nombre="Laptop HP Pavilion",
            tipo="Electrónica",
            marca="HP",
            precio=599990.00,
            activo=True
        )
        prod1.impuestos.add(iva_empresa)
        print(f"   ✓ Producto '{prod1.nombre}' creado con IVA")
        
        # Producto 2: IVA + Impuesto Específico
        prod2 = Producto.objects.create(
            empresa=empresa,
            nombre="Smartphone Samsung Galaxy",
            tipo="Electrónica",
            marca="Samsung",
            precio=399990.00,
            activo=True
        )
        prod2.impuestos.add(iva_empresa, imp_esp_empresa)
        print(f"   ✓ Producto '{prod2.nombre}' creado con IVA + Imp. Específico")
        
        # Producto 3: Sin impuestos
        prod3 = Producto.objects.create(
            empresa=empresa,
            nombre="Servicio de Consultoría",
            tipo="Servicios",
            marca="",
            precio=150000.00,
            activo=True
        )
        print(f"   ✓ Producto '{prod3.nombre}' creado sin impuestos")
    
    # 4. Crear clientes de ejemplo
    print("\n4. Creando clientes de ejemplo...")
    for empresa in empresas:
        cliente1 = Cliente.objects.create(
            empresa=empresa,
            nombre="Juan Pérez",
            rut="12345678-9",
            email="juan.perez@example.com",
            telefono="+56912345678"
        )
        print(f"   ✓ Cliente '{cliente1.nombre}' creado")
        
        cliente2 = Cliente.objects.create(
            empresa=empresa,
            nombre="María González",
            rut="98765432-1",
            email="maria.gonzalez@example.com",
            telefono="+56987654321"
        )
        print(f"   ✓ Cliente '{cliente2.nombre}' creado")

print("\n" + "=" * 60)
print("✅ POBLACIÓN COMPLETADA EXITOSAMENTE")
print("=" * 60)
print(f"\nResumen:")
print(f"  - Impuestos creados: {Impuesto.objects.count()}")
print(f"  - Productos creados: {Producto.objects.count()}")
print(f"  - Clientes creados: {Cliente.objects.count()}")
print("\n")
