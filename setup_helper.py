# Script de ayuda para configurar y ejecutar CotizApp API
# Ejecutar con: python setup_helper.py

import os
import subprocess
import sys

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, description):
    print(f"➤ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completado")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error en {description}")
        print(e.stderr)
        return False

def main():
    print_header("CotizApp API - Script de Configuración")
    
    print("Este script te ayudará a configurar el proyecto paso a paso.\n")
    
    # Paso 1: Verificar Python
    print_header("Paso 1: Verificando Python")
    python_version = sys.version_info
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} detectado")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("⚠ Se recomienda Python 3.10 o superior")
    else:
        print("✓ Versión de Python compatible")
    
    # Paso 2: Instalar dependencias
    print_header("Paso 2: Instalando Dependencias")
    respuesta = input("¿Deseas instalar las dependencias ahora? (s/n): ")
    
    if respuesta.lower() == 's':
        if not run_command("pip install -r requirements.txt", "Instalación de dependencias"):
            print("\n⚠ Hubo un error instalando las dependencias.")
            print("Intenta manualmente: pip install -r requirements.txt")
            return
    else:
        print("⏭ Saltando instalación de dependencias")
    
    # Paso 3: Configurar base de datos
    print_header("Paso 3: Configuración de Base de Datos")
    print("IMPORTANTE: Debes crear la base de datos MySQL manualmente.")
    print("\nOpciones:")
    print("1. Ejecutar en MySQL: mysql -u root -p < create_database.sql")
    print("2. Abrir MySQL Workbench y ejecutar el contenido de create_database.sql")
    print("\nAsegúrate de configurar el archivo .env con tus credenciales de MySQL:")
    print("  DB_NAME=cotizapp_db")
    print("  DB_USER=root")
    print("  DB_PASSWORD=tu_contraseña")
    
    input("\nPresiona Enter cuando hayas configurado la base de datos...")
    
    # Paso 4: Ejecutar migraciones
    print_header("Paso 4: Ejecutando Migraciones")
    respuesta = input("¿Deseas ejecutar las migraciones ahora? (s/n): ")
    
    if respuesta.lower() == 's':
        if not run_command("python manage.py migrate", "Migraciones de base de datos"):
            print("\n⚠ Error ejecutando migraciones.")
            print("Verifica que la base de datos esté creada y las credenciales en .env sean correctas")
            return
    else:
        print("⏭ Saltando migraciones")
    
    # Paso 5: Crear superusuario
    print_header("Paso 5: Crear Superusuario")
    respuesta = input("¿Deseas crear un superusuario ahora? (s/n): ")
    
    if respuesta.lower() == 's':
        print("\nSigue las instrucciones para crear el superusuario:")
        subprocess.run("python manage.py createsuperuser", shell=True)
    else:
        print("⏭ Saltando creación de superusuario")
        print("Recuerda crearlo más tarde con: python manage.py createsuperuser")
    
    # Paso 6: Iniciar servidor
    print_header("Configuración Completada")
    print("✓ El proyecto está listo para usarse")
    print("\nPara iniciar el servidor de desarrollo:")
    print("  python manage.py runserver")
    print("\nAccede a:")
    print("  - API: http://localhost:8000/api/")
    print("  - Swagger: http://localhost:8000/api/docs/")
    print("  - Admin: http://localhost:8000/admin/")
    
    respuesta = input("\n¿Deseas iniciar el servidor ahora? (s/n): ")
    
    if respuesta.lower() == 's':
        print("\nIniciando servidor...")
        print("Presiona Ctrl+C para detener el servidor\n")
        subprocess.run("python manage.py runserver", shell=True)
    else:
        print("\n¡Listo! Ejecuta 'python manage.py runserver' cuando quieras iniciar el servidor.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Script finalizado")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
