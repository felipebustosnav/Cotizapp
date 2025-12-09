import requests
import json

BASE_URL = "http://localhost:8000/api"
EMAIL = "admin@empresademo.cl"
PASSWORD = "demo123"

# Login
print("Login...")
r = requests.post(f"{BASE_URL}/auth/login/", json={"email": EMAIL, "password": PASSWORD})
token = r.json()['access']
headers = {"Authorization": f"Bearer {token}"}
print(f"Token: {token[:20]}...\n")

# Test Cliente
print("="*60)
print("TEST: Crear Cliente")
print("="*60)
payload = {
    "nombre": "Test Cliente",
    "rut": "12345678-5",
    "telefono": "+56912345678",
    "email": "test@example.com"
}
print(f"Payload: {json.dumps(payload, indent=2)}")

r = requests.post(f"{BASE_URL}/clientes/", headers=headers, json=payload)
print(f"\nStatus Code: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")

if r.status_code != 201:
    print("\n[ERROR] Cliente creation failed!")
else:
    print("\n[OK] Cliente created successfully!")
    cliente_id = r.json()['id']
    
    # Test Cotizacion
    print("\n" + "="*60)
    print("TEST: Crear Cotizacion")
    print("="*60)
    
    # Primero crear un producto
    print("\nCreando producto primero...")
    prod_payload = {
        "nombre": "Test Product",
        "tipo": "Test",
        "marca": "Test",
        "precio": "1000",
        "impuesto": "19",
        "activo": True
    }
    r = requests.post(f"{BASE_URL}/productos/", headers=headers, json=prod_payload)
    if r.status_code == 201:
        producto_id = r.json()['id']
        print(f"Producto creado: ID {producto_id}")
        
        # Ahora crear cotización
        cot_payload = {
            "cliente": cliente_id,
            "estado": "BORRADOR",
            "detalles": [
                {
                    "producto": producto_id,
                    "cantidad": 1,
                    "precio_unitario": "1000",
                    "impuesto": "19"
                }
            ]
        }
        print(f"\nPayload: {json.dumps(cot_payload, indent=2)}")
        
        r = requests.post(f"{BASE_URL}/cotizaciones/", headers=headers, json=cot_payload)
        print(f"\nStatus Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
        
        if r.status_code != 201:
            print("\n[ERROR] Cotizacion creation failed!")
        else:
            print("\n[OK] Cotizacion created successfully!")
