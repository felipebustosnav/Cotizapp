"""
Script de prueba para el sistema de impuestos dinámicos
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from django.contrib.auth import get_user_model
from empresas.models import Empresa
from impuestos.models import Impuesto, ProductoImpuesto
from productos.models import Producto

User = get_user_model()

print("=" * 70)
print("PRUEBAS DEL SISTEMA DE IMPUESTOS DINÁMICOS")
print("=" * 70)

# 1. Verificar impuestos creados
print("\n1. VERIFICANDO IMPUESTOS CREADOS")
print("-" * 70)
impuestos = Impuesto.objects.all()
print(f"Total de impuestos: {impuestos.count()}")
for imp in impuestos:
    print(f"  • {imp.nombre} ({imp.porcentaje}%) - Empresa: {imp.empresa.nombre} - Activo: {imp.activo}")

# 2. Verificar productos con impuestos
print("\n2. VERIFICANDO PRODUCTOS CON IMPUESTOS")
print("-" * 70)
productos = Producto.objects.all()
print(f"Total de productos: {productos.count()}\n")

for prod in productos:
    impuestos_prod = prod.impuestos.all()
    impuesto_total = prod.calcular_impuesto_total()
    precio_con_imp = prod.precio_con_impuesto()
    
    print(f"📦 {prod.nombre}")
    print(f"   Precio base: ${prod.precio:,.0f}")
    print(f"   Impuestos asignados: {impuestos_prod.count()}")
    for imp in impuestos_prod:
        print(f"     - {imp.nombre}: {imp.porcentaje}%")
    print(f"   Impuesto total: {impuesto_total}%")
    print(f"   Precio con impuesto: ${precio_con_imp:,.0f}")
    print()

# 3. Verificar relaciones ProductoImpuesto
print("\n3. VERIFICANDO RELACIONES PRODUCTO-IMPUESTO")
print("-" * 70)
relaciones = ProductoImpuesto.objects.all()
print(f"Total de relaciones: {relaciones.count()}")
for rel in relaciones:
    print(f"  • {rel.producto.nombre} ← {rel.impuesto.nombre} (Orden: {rel.orden})")

# 4. Prueba de cálculo de impuestos
print("\n4. PRUEBA DE CÁLCULO DE IMPUESTOS")
print("-" * 70)
if productos.exists():
    producto_prueba = productos.first()
    print(f"Producto de prueba: {producto_prueba.nombre}")
    print(f"Precio base: ${producto_prueba.precio:,.0f}")
    
    impuestos_aplicados = producto_prueba.impuestos.filter(activo=True)
    print(f"\nImpuestos aplicados ({impuestos_aplicados.count()}):")
    total_manual = 0
    for imp in impuestos_aplicados:
        print(f"  + {imp.nombre}: {imp.porcentaje}%")
        total_manual += float(imp.porcentaje)
    
    total_calculado = float(producto_prueba.calcular_impuesto_total())
    print(f"\nTotal manual: {total_manual}%")
    print(f"Total calculado: {total_calculado}%")
    print(f"✓ Cálculo correcto: {total_manual == total_calculado}")
    
    precio_final = float(producto_prueba.precio_con_impuesto())
    precio_esperado = float(producto_prueba.precio) * (1 + total_calculado / 100)
    print(f"\nPrecio final: ${precio_final:,.0f}")
    print(f"Precio esperado: ${precio_esperado:,.0f}")
    print(f"✓ Precio correcto: {abs(precio_final - precio_esperado) < 0.01}")

# 5. Verificar que productos sin impuestos funcionan
print("\n5. VERIFICANDO PRODUCTOS SIN IMPUESTOS")
print("-" * 70)
productos_sin_imp = [p for p in productos if p.impuestos.count() == 0]
if productos_sin_imp:
    for prod in productos_sin_imp:
        print(f"  • {prod.nombre}")
        print(f"    Impuesto total: {prod.calcular_impuesto_total()}%")
        print(f"    Precio: ${prod.precio:,.0f} → ${prod.precio_con_impuesto():,.0f}")
else:
    print("  No hay productos sin impuestos")

# 6. Resumen de empresas
print("\n6. RESUMEN POR EMPRESA")
print("-" * 70)
empresas = Empresa.objects.all()
for empresa in empresas:
    print(f"\n🏢 {empresa.nombre}")
    print(f"   Impuestos: {empresa.impuestos.count()}")
    print(f"   Productos: {empresa.productos.count()}")
    productos_con_imp = sum(1 for p in empresa.productos.all() if p.impuestos.count() > 0)
    print(f"   Productos con impuestos: {productos_con_imp}")

print("\n" + "=" * 70)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 70)
