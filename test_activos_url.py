"""
Script para probar el endpoint de impuestos activos
"""
import requests

BASE_URL = "http://localhost:8000/api"

# Login
login_data = {
    "email": "admin@empresademo.cl",
    "password": "demo123"
}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
token = response.json()['access']
headers = {"Authorization": f"Bearer {token}"}

# Probar diferentes URLs
urls_to_test = [
    "/impuestos/activos/",
    "/impuestos/activos",
    "/api/impuestos/activos/",
    "/api/impuestos/activos",
]

print("Probando URLs para impuestos activos:\n")
for url in urls_to_test:
    full_url = f"http://localhost:8000{url}" if url.startswith('/api') else f"{BASE_URL}{url}"
    try:
        response = requests.get(full_url, headers=headers)
        print(f"✓ {full_url} → Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Data: {response.json()[:100] if len(str(response.json())) > 100 else response.json()}")
    except Exception as e:
        print(f"✗ {full_url} → Error: {str(e)[:50]}")
