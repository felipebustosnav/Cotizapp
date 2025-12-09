import requests
import json

BASE_URL = "http://localhost:8000/api"
SUPERUSER_EMAIL = "admin@cotizapp.com"
SUPERUSER_PASSWORD = "admin123"

def debug_settings():
    print("Obteniendo token...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json={"email": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD}
        )
        if response.status_code != 200:
            print(f"Error login: {response.status_code} {response.text}")
            return

        token = response.json()['access']
        print("Token OK")
        
        print("\nProbando GET /empresa/mi_empresa/ ...")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/empresa/mi_empresa/", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Data recibida:")
            print(json.dumps(data, indent=2))
            
            if 'autoaprobar_cotizaciones' in data:
                print("\n[OK] Campo 'autoaprobar_cotizaciones' presente.")
            else:
                print("\n[ERROR] Campo 'autoaprobar_cotizaciones' NO presente en la respuesta.")
        else:
            print(f"Error response: {response.text}")

    except Exception as e:
        print(f"Excepción: {e}")

if __name__ == "__main__":
    debug_settings()
