"""
Script de prueba simple para verificar un endpoint especifico
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"
EMAIL = "admin@cotizapp.com"
PASSWORD = "admin123"

# Login
print("1. Login...")
response = requests.post(f"{BASE_URL}/auth/login/", json={"email": EMAIL, "password": PASSWORD})
print(f"   Status: {response.status_code}")
if response.status_code != 200:
    print(f"   Error: {response.text}")
    exit(1)

token = response.json()['access']
print(f"   Token OK")

headers = {"Authorization": f"Bearer {token}"}

# Crear producto
print("\n2. Crear producto...")
response = requests.post(
    f"{BASE_URL}/productos/",
    headers=headers,
    json={
        "nombre": "Test Product",
        "tipo": "Test",
        "marca": "Test",
        "precio": "1000",
        "impuesto": "19",
        "activo": True
    }
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code == 201:
    print("   [OK] Producto creado!")
    producto_id = response.json()['id']
    print(f"   ID: {producto_id}")
else:
    print("   [ERROR] No se pudo crear producto")

# Crear cliente
print("\n3. Crear cliente...")
response = requests.post(
    f"{BASE_URL}/clientes/",
    headers=headers,
    json={
        "nombre": "Test Client",
        "rut": "11111111-1",
        "telefono": "+56911111111",
        "email": "test@client.com"
    }
)
print(f"   Status: {response.status_code}")
print(f"   Response: {response.text}")

if response.status_code == 201:
    print("   [OK] Cliente creado!")
    cliente_id = response.json()['id']
    print(f"   ID: {cliente_id}")
else:
    print("   [ERROR] No se pudo crear cliente")
