import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from usuarios.models import Usuario
from empresas.models import Empresa

def check_superuser_status():
    print("Iniciando chequeo de superusuarios...")
    try:
        admins = Usuario.objects.filter(is_superuser=True)
        print(f"Superusuarios encontrados: {admins.count()}")
        
        for admin in admins:
            empresa_nombre = admin.empresa.nombre if admin.empresa else "None"
            print(f"User: {admin.email}, Empresa: {empresa_nombre}")
            
        empresas = Empresa.objects.all()
        print(f"Total empresas: {empresas.count()}")
        
        if not empresas.exists():
            print("No hay empresas en el sistema. Creando una empresa por defecto...")
            empresa = Empresa.objects.create(
                nombre="Empresa Principal", 
                rut="76.123.456-7", 
                email="contacto@empresa.cl"
            )
            print(f"Empresa creada: {empresa.nombre}")
        else:
            empresa = empresas.first()
            print(f"Usando empresa existente: {empresa.nombre} (ID: {empresa.id})")

        # Asignar empresa a admins sin empresa
        for admin in admins:
            if not admin.empresa:
                print(f"Asignando empresa {empresa.nombre} al superusuario {admin.email}")
                admin.empresa = empresa
                admin.save()
                print("Asignación completada.")
            else:
                print(f"Superusuario {admin.email} ya tiene empresa asignada.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_superuser_status()
