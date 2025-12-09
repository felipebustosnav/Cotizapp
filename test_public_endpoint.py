"""
Test del endpoint público de autoatención
"""
import requests

BASE_URL = "http://localhost:8000/api"

# Obtener slug de la empresa demo
print("1. Obteniendo información de empresa...")
response = requests.get(f"{BASE_URL}/autoatencion/empresa-demo-XXXXXXXX/")
print(f"Status: {response.status_code}")

if response.status_code == 404:
    # Necesitamos obtener el slug real
    print("\nObteniendo slug real de empresa...")
    # Login como admin
    login_response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"email": "admin@empresademo.cl", "password": "demo123"}
    )
    token = login_response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Obtener empresa
    empresa_response = requests.get(f"{BASE_URL}/empresa/mi_empresa/", headers=headers)
    if empresa_response.status_code == 200:
        empresa_data = empresa_response.json()
        slug = empresa_data['slug_autoatencion']
        print(f"Slug encontrado: {slug}")
        
        # Probar endpoint público
        print(f"\n2. Probando endpoint público...")
        public_response = requests.get(f"{BASE_URL}/autoatencion/{slug}/")
        print(f"Status: {public_response.status_code}")
        
        if public_response.status_code == 200:
            data = public_response.json()
            print(f"\nEmpresa: {data['empresa']['nombre']}")
            print(f"Productos disponibles: {len(data['productos'])}")
            
            if data['productos']:
                print("\n3. Creando cotización pública...")
                producto_id = data['productos'][0]['id']
                
                cotizacion_data = {
                    "cliente_nombre": "Cliente Público Test",
                    "cliente_email": "publico@test.com",
                    "cliente_telefono": "+56900000000",
                    "detalles": [
                        {
                            "producto_id": producto_id,
                            "cantidad": 2
                        }
                    ],
                    "notas": "Cotización de prueba desde autoatención"
                }
                
                cotizar_response = requests.post(
                    f"{BASE_URL}/autoatencion/{slug}/cotizar/",
                    json=cotizacion_data
                )
                print(f"Status: {cotizar_response.status_code}")
                print(f"Response: {cotizar_response.json()}")
                
                if cotizar_response.status_code == 201:
                    print("\n✅ Endpoint público funcionando correctamente!")
                else:
                    print("\n❌ Error al crear cotización pública")
        else:
            print(f"Error: {public_response.text}")
