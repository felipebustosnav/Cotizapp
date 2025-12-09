"""
Script de pruebas simplificado para la API de CotizApp.
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"
SUPERUSER_EMAIL = "admin@cotizapp.com"
SUPERUSER_PASSWORD = "admin123"

# Variables globales
token = None
empresa_id = None
producto_id = None
cliente_id = None
cotizacion_id = None

def test_login():
    global token
    print("\n1. Probando autenticacion...")
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()['access']
        print(f"   [OK] Token obtenido")
        return True
    print(f"   [ERROR] Login fallo: {response.status_code}")
    return False

def test_create_empresa():
    global empresa_id
    print("\n2. Creando empresa...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/empresa/",
        headers=headers,
        json={
            "nombre": "Empresa Test",
            "rut": "76123456-7",
            "direccion": "Av. Test 123",
            "telefono": "+56912345678",
            "email": "test@empresa.cl"
        }
    )
    if response.status_code == 201:
        empresa_id = response.json()['id']
        print(f"   [OK] Empresa creada con ID: {empresa_id}")
        return True
    print(f"   [ERROR] {response.status_code}: {response.text}")
    return False

def test_create_producto():
    global producto_id
    print("\n3. Creando producto...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/productos/",
        headers=headers,
        json={
            "nombre": "Laptop Test",
            "tipo": "Computadores",
            "marca": "HP",
            "precio": "500000",
            "impuesto": "19",
            "activo": True,
            "empresa": empresa_id
        }
    )
    if response.status_code == 201:
        producto_id = response.json()['id']
        print(f"   [OK] Producto creado con ID: {producto_id}")
        return True
    print(f"   [ERROR] {response.status_code}: {response.text}")
    return False

def test_create_cliente():
    global cliente_id
    print("\n4. Creando cliente...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/clientes/",
        headers=headers,
        json={
            "nombre": "Cliente Test",
            "rut": "12345678-5",
            "telefono": "+56987654321",
            "email": "cliente@test.cl",
            "empresa": empresa_id
        }
    )
    if response.status_code == 201:
        cliente_id = response.json()['id']
        print(f"   [OK] Cliente creado con ID: {cliente_id}")
        return True
    print(f"   [ERROR] {response.status_code}: {response.text}")
    return False

def test_create_cotizacion():
    global cotizacion_id
    print("\n5. Creando cotizacion...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/cotizaciones/",
        headers=headers,
        json={
            "cliente": cliente_id,
            "empresa": empresa_id,
            "estado": "BORRADOR",
            "detalles": [
                {
                    "producto": producto_id,
                    "cantidad": 2,
                    "precio_unitario": "500000",
                    "impuesto": "19"
                }
            ]
        }
    )
    if response.status_code == 201:
        data = response.json()
        cotizacion_id = data['id']
        print(f"   [OK] Cotizacion creada: {data['numero']}")
        print(f"   Total: ${data['total']}")
        return True
    print(f"   [ERROR] {response.status_code}: {response.text}")
    return False

def test_get_pdf():
    print("\n6. Generando PDF...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/cotizaciones/{cotizacion_id}/pdf/",
        headers=headers
    )
    if response.status_code == 200:
        print(f"   [OK] PDF generado ({len(response.content)} bytes)")
        return True
    print(f"   [ERROR] {response.status_code}")
    return False

def test_list_all():
    print("\n7. Listando recursos...")
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("Productos", f"{BASE_URL}/productos/"),
        ("Clientes", f"{BASE_URL}/clientes/"),
        ("Cotizaciones", f"{BASE_URL}/cotizaciones/")
    ]
    
    all_ok = True
    for name, url in endpoints:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            count = len(response.json().get('results', []))
            print(f"   [OK] {name}: {count} items")
        else:
            print(f"   [ERROR] {name}: {response.status_code}")
            all_ok = False
    return all_ok

def test_search():
    print("\n8. Probando busqueda...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/productos/?search=Laptop",
        headers=headers
    )
    if response.status_code == 200:
        print(f"   [OK] Busqueda funciona")
        return True
    print(f"   [ERROR] {response.status_code}")
    return False

def run_tests():
    print("="*60)
    print("  PRUEBAS API COTIZAPP")
    print("="*60)
    
    tests = [
        test_login,
        test_create_empresa,
        test_create_producto,
        test_create_cliente,
        test_create_cotizacion,
        test_get_pdf,
        test_list_all,
        test_search
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   [ERROR CRITICO] {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("\n[EXITO] Todas las pruebas pasaron!")
    else:
        print("\n[ATENCION] Algunas pruebas fallaron")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\nError critico: {e}")
        exit(1)
