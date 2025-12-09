"""
Script de pruebas automatizadas para la API de CotizApp.
Verifica que todos los endpoints principales funcionen correctamente.
"""
import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = "http://localhost:8000/api"
SUPERUSER_EMAIL = "admin@cotizapp.com"
SUPERUSER_PASSWORD = "admin123"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, details=""):
    """Imprime resultado de una prueba"""
    symbol = "✓" if status else "✗"
    color = Colors.GREEN if status else Colors.RED
    print(f"{color}{symbol} {name}{Colors.END}")
    if details:
        print(f"  {details}")

def print_section(name):
    """Imprime encabezado de sección"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}{Colors.END}\n")

# Variables globales para almacenar IDs
token = None
empresa_id = None
producto_id = None
cliente_id = None
cotizacion_id = None
admin_empresa_id = None

def test_authentication():
    """Prueba 1: Autenticación JWT"""
    global token
    print_section("1. AUTENTICACIÓN JWT")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json={
                "email": SUPERUSER_EMAIL,
                "password": SUPERUSER_PASSWORD
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print_test("Login exitoso", True, f"Token obtenido: {token[:20]}...")
            print_test("Token de refresh obtenido", 'refresh' in data)
            return True
        else:
            print_test("Login fallido", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Error en autenticación", False, str(e))
        return False

def test_create_empresa():
    """Prueba 2: Crear Empresa"""
    global empresa_id
    print_section("2. CREAR EMPRESA")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/empresa/",
            headers=headers,
            json={
                "nombre": "Empresa de Prueba S.A.",
                "rut": "76123456-7",
                "direccion": "Av. Principal 123, Santiago",
                "telefono": "+56912345678",
                "email": "contacto@empresaprueba.cl"
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            empresa_id = data.get('id')
            print_test("Empresa creada", True, f"ID: {empresa_id}")
            print_test("Slug de autoatención generado", 'slug_autoatencion' in data)
            return True
        else:
            print_test("Error al crear empresa", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_test("Error en creación de empresa", False, str(e))
        return False

def test_create_admin_empresa():
    """Prueba 3: Crear Administrador de Empresa"""
    global admin_empresa_id
    print_section("3. CREAR ADMINISTRADOR DE EMPRESA")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/usuarios/",
            headers=headers,
            json={
                "email": "admin@empresaprueba.cl",
                "username": "admin_empresa",
                "first_name": "Juan",
                "last_name": "Pérez",
                "rol": "ADMIN",
                "empresa": empresa_id,
                "password": "admin123",
                "confirm_password": "admin123"
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            admin_empresa_id = data.get('id')
            print_test("Admin de empresa creado", True, f"ID: {admin_empresa_id}")
            print_test("Rol asignado correctamente", data.get('rol') == 'ADMIN')
            return True
        else:
            print_test("Error al crear admin", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_test("Error en creación de admin", False, str(e))
        return False

def test_create_producto():
    """Prueba 4: Crear Producto"""
    global producto_id
    print_section("4. CREAR PRODUCTO")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/productos/",
            headers=headers,
            json={
                "nombre": "Laptop HP Pavilion",
                "tipo": "Computadores",
                "marca": "HP",
                "precio": "599990",
                "impuesto": "19",
                "activo": True,
                "empresa": empresa_id
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            producto_id = data.get('id')
            print_test("Producto creado", True, f"ID: {producto_id}")
            print_test("Precio con impuesto calculado", 'precio_con_impuesto' in data)
            return True
        else:
            print_test("Error al crear producto", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_test("Error en creación de producto", False, str(e))
        return False

def test_create_cliente():
    """Prueba 5: Crear Cliente"""
    global cliente_id
    print_section("5. CREAR CLIENTE")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/clientes/",
            headers=headers,
            json={
                "nombre": "María González",
                "rut": "12345678-5",
                "telefono": "+56987654321",
                "email": "maria@cliente.cl",
                "empresa": empresa_id
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            cliente_id = data.get('id')
            print_test("Cliente creado", True, f"ID: {cliente_id}")
            print_test("RUT formateado", 'rut_formateado' in data)
            return True
        else:
            print_test("Error al crear cliente", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_test("Error en creación de cliente", False, str(e))
        return False

def test_create_cotizacion():
    """Prueba 6: Crear Cotización"""
    global cotizacion_id
    print_section("6. CREAR COTIZACIÓN")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/cotizaciones/",
            headers=headers,
            json={
                "cliente": cliente_id,
                "empresa": empresa_id,
                "estado": "BORRADOR",
                "notas": "Cotización de prueba",
                "detalles": [
                    {
                        "producto": producto_id,
                        "cantidad": 2,
                        "precio_unitario": "599990",
                        "impuesto": "19"
                    }
                ]
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            cotizacion_id = data.get('id')
            print_test("Cotización creada", True, f"Número: {data.get('numero')}")
            print_test("Totales calculados", data.get('total') > 0)
            print_test("Detalles incluidos", len(data.get('detalles', [])) > 0)
            return True
        else:
            print_test("Error al crear cotización", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print_test("Error en creación de cotización", False, str(e))
        return False

def test_get_cotizacion_pdf():
    """Prueba 7: Generar PDF de Cotización"""
    print_section("7. GENERAR PDF DE COTIZACIÓN")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/cotizaciones/{cotizacion_id}/pdf/",
            headers=headers
        )
        
        if response.status_code == 200:
            print_test("PDF generado", True, f"Tamaño: {len(response.content)} bytes")
            print_test("Content-Type correcto", response.headers.get('Content-Type') == 'application/pdf')
            return True
        else:
            print_test("Error al generar PDF", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Error en generación de PDF", False, str(e))
        return False

def test_list_endpoints():
    """Prueba 8: Listar recursos"""
    print_section("8. LISTAR RECURSOS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("Usuarios", f"{BASE_URL}/usuarios/"),
        ("Empresas", f"{BASE_URL}/empresa/"),
        ("Productos", f"{BASE_URL}/productos/"),
        ("Clientes", f"{BASE_URL}/clientes/"),
        ("Cotizaciones", f"{BASE_URL}/cotizaciones/")
    ]
    
    all_success = True
    for name, url in endpoints:
        try:
            response = requests.get(url, headers=headers)
            success = response.status_code == 200
            print_test(f"Listar {name}", success, f"Encontrados: {len(response.json().get('results', []))} items")
            all_success = all_success and success
        except Exception as e:
            print_test(f"Listar {name}", False, str(e))
            all_success = False
    
    return all_success

def test_search_and_filter():
    """Prueba 9: Búsqueda y Filtros"""
    print_section("9. BÚSQUEDA Y FILTROS")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Buscar producto
        response = requests.get(
            f"{BASE_URL}/productos/?search=Laptop",
            headers=headers
        )
        print_test("Búsqueda de productos", response.status_code == 200)
        
        # Filtrar productos activos
        response = requests.get(
            f"{BASE_URL}/productos/?activo=true",
            headers=headers
        )
        print_test("Filtro de productos activos", response.status_code == 200)
        
        # Filtrar cotizaciones por estado
        response = requests.get(
            f"{BASE_URL}/cotizaciones/?estado=BORRADOR",
            headers=headers
        )
        print_test("Filtro de cotizaciones por estado", response.status_code == 200)
        
        return True
    except Exception as e:
        print_test("Error en búsqueda/filtros", False, str(e))
        return False

def test_permissions():
    """Prueba 10: Permisos"""
    print_section("10. VERIFICACIÓN DE PERMISOS")
    
    # Intentar acceder sin token
    try:
        response = requests.get(f"{BASE_URL}/productos/")
        print_test("Acceso sin autenticación bloqueado", response.status_code == 401)
    except Exception as e:
        print_test("Error en prueba de permisos", False, str(e))
        return False
    
    return True

def run_all_tests():
    """Ejecuta todas las pruebas"""
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("  PRUEBAS AUTOMATIZADAS - API COTIZAPP")
    print(f"{'='*60}{Colors.END}\n")
    print(f"Servidor: {BASE_URL}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("Autenticación", test_authentication),
        ("Crear Empresa", test_create_empresa),
        ("Crear Admin Empresa", test_create_admin_empresa),
        ("Crear Producto", test_create_producto),
        ("Crear Cliente", test_create_cliente),
        ("Crear Cotización", test_create_cotizacion),
        ("Generar PDF", test_get_cotizacion_pdf),
        ("Listar Recursos", test_list_endpoints),
        ("Búsqueda y Filtros", test_search_and_filter),
        ("Permisos", test_permissions)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_test(f"Error crítico en {name}", False, str(e))
            results.append((name, False))
    
    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BLUE}Resultado: {passed}/{total} pruebas exitosas{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ ¡Todas las pruebas pasaron exitosamente!{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}⚠ Algunas pruebas fallaron. Revisa los detalles arriba.{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas interrumpidas por el usuario{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error crítico: {e}{Colors.END}")
        exit(1)
