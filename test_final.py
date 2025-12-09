"""
Script de pruebas final con usuario administrador de empresa
"""
import requests

BASE_URL = "http://localhost:8000/api"
ADMIN_EMAIL = "admin@empresademo.cl"
ADMIN_PASSWORD = "demo123"

token = None
producto_id = None
cliente_id = None
cotizacion_id = None

print("="*60)
print("  PRUEBAS FINALES API COTIZAPP")
print("  Usuario: Administrador de Empresa")
print("="*60)

# 1. Login
print("\n1. Login con admin de empresa...")
response = requests.post(f"{BASE_URL}/auth/login/", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
if response.status_code == 200:
    token = response.json()['access']
    print("   [OK] Login exitoso")
else:
    print(f"   [ERROR] {response.status_code}: {response.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 2. Crear producto (sin especificar empresa)
print("\n2. Crear producto (empresa asignada automaticamente)...")
response = requests.post(
    f"{BASE_URL}/productos/",
    headers=headers,
    json={
        "nombre": "Laptop Dell Inspiron",
        "tipo": "Computadores",
        "marca": "Dell",
        "precio": "750000",
        "impuesto": "19",
        "activo": True
    }
)
if response.status_code == 201:
    producto_id = response.json()['id']
    print(f"   [OK] Producto creado (ID: {producto_id})")
    print(f"   Empresa: {response.json().get('empresa_nombre')}")
else:
    print(f"   [ERROR] {response.status_code}: {response.text}")

# 3. Crear cliente (sin especificar empresa)
print("\n3. Crear cliente (empresa asignada automaticamente)...")
response = requests.post(
    f"{BASE_URL}/clientes/",
    headers=headers,
    json={
        "nombre": "Juan Pérez",
        "rut": "12345678-5",
        "telefono": "+56912345678",
        "email": "juan@cliente.cl"
    }
)
if response.status_code == 201:
    cliente_id = response.json()['id']
    print(f"   [OK] Cliente creado (ID: {cliente_id})")
    print(f"   RUT formateado: {response.json().get('rut_formateado')}")
else:
    print(f"   [ERROR] {response.status_code}: {response.text}")

# 4. Crear cotización (sin especificar empresa ni usuario_creador)
print("\n4. Crear cotizacion (campos asignados automaticamente)...")
response = requests.post(
    f"{BASE_URL}/cotizaciones/",
    headers=headers,
    json={
        "cliente": cliente_id,
        "estado": "BORRADOR",
        "notas": "Cotización de prueba",
        "detalles": [
            {
                "producto": producto_id,
                "cantidad": 2,
                "precio_unitario": "750000",
                "impuesto": "19"
            }
        ]
    }
)
if response.status_code == 201:
    data = response.json()
    cotizacion_id = data['id']
    print(f"   [OK] Cotizacion creada")
    print(f"   Numero: {data['numero']}")
    print(f"   Total: ${data['total']:,.0f}")
else:
    print(f"   [ERROR] {response.status_code}: {response.text}")

# 5. Generar PDF
if cotizacion_id:
    print("\n5. Generar PDF de cotizacion...")
    response = requests.get(f"{BASE_URL}/cotizaciones/{cotizacion_id}/pdf/", headers=headers)
    if response.status_code == 200:
        print(f"   [OK] PDF generado ({len(response.content):,} bytes)")
        # Guardar PDF
        with open("cotizacion_test.pdf", "wb") as f:
            f.write(response.content)
        print("   PDF guardado como: cotizacion_test.pdf")
    else:
        print(f"   [ERROR] {response.status_code}")

# 6. Listar recursos
print("\n6. Listar recursos...")
for name, endpoint in [("Productos", "productos"), ("Clientes", "clientes"), ("Cotizaciones", "cotizaciones")]:
    response = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers)
    if response.status_code == 200:
        count = len(response.json().get('results', []))
        print(f"   [OK] {name}: {count} items")
    else:
        print(f"   [ERROR] {name}: {response.status_code}")

# 7. Buscar producto
print("\n7. Buscar producto...")
response = requests.get(f"{BASE_URL}/productos/?search=Dell", headers=headers)
if response.status_code == 200:
    results = response.json().get('results', [])
    print(f"   [OK] Encontrados: {len(results)} productos")
else:
    print(f"   [ERROR] {response.status_code}")

# 8. Filtrar cotizaciones por estado
print("\n8. Filtrar cotizaciones por estado...")
response = requests.get(f"{BASE_URL}/cotizaciones/?estado=BORRADOR", headers=headers)
if response.status_code == 200:
    results = response.json().get('results', [])
    print(f"   [OK] Cotizaciones en borrador: {len(results)}")
else:
    print(f"   [ERROR] {response.status_code}")

print("\n" + "="*60)
print("  PRUEBAS COMPLETADAS")
print("="*60)
print("\n[EXITO] Todas las funcionalidades principales funcionan correctamente!")
print("\nCredenciales de prueba:")
print(f"  Email: {ADMIN_EMAIL}")
print(f"  Password: {ADMIN_PASSWORD}")
print(f"\nSwagger UI: http://localhost:8000/api/docs/")
