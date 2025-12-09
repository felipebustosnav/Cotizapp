import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from empresas.models import Empresa

BASE_URL = "http://localhost:8000/api"

def debug_public_link():
    print("1. Checking Database for Slug...")
    empresa = Empresa.objects.first()
    if not empresa:
        print("No empresa found!")
        return

    print(f"Empresa: {empresa.nombre}")
    print(f"Slug: '{empresa.slug_autoatencion}'")

    if not empresa.slug_autoatencion:
        print("Slug is missing! Attempting to fix...")
        empresa.save() # trigger save method validation
        print(f"New Slug: '{empresa.slug_autoatencion}'")
    
    slug = empresa.slug_autoatencion
    
    # 2. Testing API Endpoint
    url = f"{BASE_URL}/autoatencion/{slug}/"
    print(f"2. Testing API: {url}")
    
    try:
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Response OK")
            print(f"Empresa Name in JSON: {data.get('empresa', {}).get('nombre')}")
            print(f"Products Count: {len(data.get('productos', []))}")
        else:
            print(f"Error: {resp.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_public_link()
