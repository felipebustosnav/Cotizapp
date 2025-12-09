
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from usuarios.models import Usuario
from empresas.models import Empresa

def reset_admin():
    email = 'admin@empresademo.cl'
    password = 'demo123'
    
    # 1. Asegurar que existe la empresa
    empresa, created = Empresa.objects.get_or_create(
        rut='76.123.456-7',
        defaults={
            'nombre': 'Empresa Demo SpA',
            'direccion': 'Av. Siempre Viva 123',
            'telefono': '+56912345678',
            'email': 'contacto@empresademo.cl'
        }
    )
    if created:
        print(f"Empresa creada: {empresa.nombre}")
    else:
        print(f"Empresa encontrada: {empresa.nombre}")

    # 2. Buscar o crear usuario admin
    try:
        user = Usuario.objects.get(email=email)
        print(f"Usuario {email} encontrado. Actualizando password...")
        user.set_password(password)
        
        # 3. Vincular empresa si no tiene
        if not user.empresa:
            print("Asignando empresa al usuario...")
            user.empresa = empresa
        
        user.rol = Usuario.Rol.ADMINISTRADOR
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print("Password actualizado y empresa vinculada exitosamente.")
        
    except Usuario.DoesNotExist:
        print(f"Usuario {email} no existe. Creando...")
        user = Usuario.objects.create_superuser(
            email=email,
            username='admin',
            first_name='Admin',
            last_name='Demo',
            password=password,
            empresa=empresa,  # Vincular al crear
            rol=Usuario.Rol.ADMINISTRADOR
        )
        print("Usuario creado exitosamente.")

if __name__ == '__main__':
    reset_admin()
