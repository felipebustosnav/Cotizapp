import requests
import json

BASE_URL = "http://localhost:8000/api"
SUPERUSER_EMAIL = "admin@cotizapp.com"
SUPERUSER_PASSWORD = "admin123"

def test_client_crud():
    print("1. Login...")
    try:
        auth_resp = requests.post(
            f"{BASE_URL}/auth/login/",
            json={"email": SUPERUSER_EMAIL, "password": SUPERUSER_PASSWORD}
        )
        if auth_resp.status_code != 200:
            print(f"Login failed: {auth_resp.text}")
            return
        
        token = auth_resp.json()['access']
        headers = {"Authorization": f"Bearer {token}"}
        print("Login OK")

        # 2. Obteniendo ID de empresa (necesario para superuser si no tiene una asignada por defecto)
        # O en este caso, el viewset asigna la del usuario. Intentaremos sin enviar empresa primero (asumiendo usuario normal)
        # O si es superuser, necesitamos enviar empresa.
        
        # Primero verificamos si el usuario tiene empresa.
        me_resp = requests.get(f"{BASE_URL}/empresa/mi_empresa/", headers=headers)
        empresa_id = None
        if me_resp.status_code == 200:
             empresa_id = me_resp.json()['id']
             print(f"Usuario tiene empresa asignada: {empresa_id}")
        else:
             print("Usuario no tiene empresa asignada o es superuser sin link.")
             # Listar empresas para usar una
             emp_list = requests.get(f"{BASE_URL}/empresa/", headers=headers)
             if emp_list.status_code == 200 and len(emp_list.json()) > 0:
                 empresa_id = emp_list.json()[0]['id']
                 print(f"Usando primera empresa encontrada: {empresa_id}")

        client_data = {
            "nombre": "Cliente Test Script",
            "rut": "11111111-1", # RUT invalido intencionalmente para ver error? No, usar valido probemos 1-9
            "rut": "16000000-k", # Rut que deberia ser valido? OJO: Formatter usa mayusculas
            "email": "testclient@example.com",
            "telefono": "+56912345678",
            "direccion": "Calle Falsa 123"
        }
        
        if empresa_id:
             print(f"Usuario tiene empresa asignada (ID {empresa_id}), pero NO la enviaremos para probar el fix del backend.")
             # client_data['empresa'] = empresa_id  <-- Comentado para simular frontend

        print(f"3. Creando cliente payload: {client_data}")
        resp = requests.post(f"{BASE_URL}/clientes/", json=client_data, headers=headers)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
        
    except Exception as e:
        print(f"Excepción: {e}")

if __name__ == "__main__":
    test_client_crud()
