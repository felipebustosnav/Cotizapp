"""
Script para probar los endpoints de la API de impuestos
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# Obtener token de autenticación
print("=" * 70)
print("PRUEBAS DE API - SISTEMA DE IMPUESTOS")
print("=" * 70)

print("\n1. AUTENTICACIÓN")
print("-" * 70)
login_data = {
    "email": "admin@empresademo.cl",
    "password": "demo123"
}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
if response.status_code == 200:
    token = response.json()['access']
    print("✓ Login exitoso")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"✗ Error en login: {response.status_code}")
    exit(1)

# 2. Listar todos los impuestos
print("\n2. GET /api/impuestos/ - Listar todos los impuestos")
print("-" * 70)
response = requests.get(f"{BASE_URL}/impuestos/", headers=headers)
if response.status_code == 200:
    data = response.json()
    # Manejar respuesta paginada o lista directa
    impuestos = data if isinstance(data, list) else data.get('results', data)
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Total de impuestos: {len(impuestos)}")
    for imp in list(impuestos)[:3]:  # Mostrar primeros 3
        print(f"  • {imp['nombre']}: {imp['porcentaje']}% (Activo: {imp['activo']})")
else:
    print(f"✗ Error: {response.status_code}")

# 3. Listar solo impuestos activos
print("\n3. GET /api/impuestos/activos/ - Listar impuestos activos")
print("-" * 70)
response = requests.get(f"{BASE_URL}/impuestos/activos/", headers=headers)
if response.status_code == 200:
    impuestos_activos = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Impuestos activos: {len(impuestos_activos)}")
    for imp in impuestos_activos:
        print(f"  • {imp['nombre']}: {imp['porcentaje']}%")
else:
    print(f"✗ Error: {response.status_code}")

# 4. Crear nuevo impuesto
print("\n4. POST /api/impuestos/ - Crear nuevo impuesto")
print("-" * 70)
nuevo_impuesto = {
    "nombre": "Impuesto de Prueba",
    "porcentaje": 10.00,
    "activo": True
}
response = requests.post(f"{BASE_URL}/impuestos/", json=nuevo_impuesto, headers=headers)
if response.status_code == 201:
    impuesto_creado = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Impuesto creado: {impuesto_creado['nombre']} (ID: {impuesto_creado['id']})")
    impuesto_id = impuesto_creado['id']
else:
    print(f"✗ Error: {response.status_code} - {response.text}")
    impuesto_id = None

# 5. Actualizar impuesto
if impuesto_id:
    print("\n5. PUT /api/impuestos/{id}/ - Actualizar impuesto")
    print("-" * 70)
    actualizar_data = {
        "nombre": "Impuesto de Prueba Actualizado",
        "porcentaje": 12.50,
        "activo": True
    }
    response = requests.put(f"{BASE_URL}/impuestos/{impuesto_id}/", json=actualizar_data, headers=headers)
    if response.status_code == 200:
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Impuesto actualizado: {response.json()['nombre']} - {response.json()['porcentaje']}%")
    else:
        print(f"✗ Error: {response.status_code}")

# 6. Listar productos con impuestos
print("\n6. GET /api/productos/ - Listar productos con impuestos")
print("-" * 70)
response = requests.get(f"{BASE_URL}/productos/", headers=headers)
if response.status_code == 200:
    data = response.json()
    productos = data if isinstance(data, list) else data.get('results', data)
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Total de productos: {len(productos)}")
    for prod in list(productos)[:3]:  # Mostrar primeros 3
        print(f"\n  📦 {prod['nombre']}")
        print(f"     Precio: ${prod['precio']}")
        print(f"     Impuesto total: {prod.get('impuesto_total', 0)}%")
        print(f"     Precio con impuesto: ${prod.get('precio_con_impuesto', 0)}")
        if 'impuestos' in prod and prod['impuestos']:
            print(f"     Impuestos aplicados:")
            for imp in prod['impuestos']:
                print(f"       - {imp['nombre']}: {imp['porcentaje']}%")
else:
    print(f"✗ Error: {response.status_code}")

# 7. Eliminar impuesto de prueba
if impuesto_id:
    print("\n7. DELETE /api/impuestos/{id}/ - Eliminar impuesto")
    print("-" * 70)
    response = requests.delete(f"{BASE_URL}/impuestos/{impuesto_id}/", headers=headers)
    if response.status_code == 204:
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Impuesto eliminado correctamente")
    else:
        print(f"✗ Error: {response.status_code}")

print("\n" + "=" * 70)
print("✅ PRUEBAS DE API COMPLETADAS")
print("=" * 70)
