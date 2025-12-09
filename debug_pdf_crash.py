import os
import django
import sys
import traceback

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from cotizaciones.models import Cotizacion
from cotizaciones.utils.pdf_generator import generar_pdf_cotizacion

def debug_crash(cotizacion_id):
    try:
        cotizacion = Cotizacion.objects.get(pk=cotizacion_id)
        print(f"Testing PDF for ID: {cotizacion.id}, Numero: {cotizacion.numero}")
        print(f"Empresa: {cotizacion.empresa.nombre} (ID: {cotizacion.empresa.id})")
        print(f"Logo: {cotizacion.empresa.logo}")
        
        pdf = generar_pdf_cotizacion(cotizacion)
        print("Success!")
    except Cotizacion.DoesNotExist:
        print(f"Cotizacion {cotizacion_id} not found")
    except Exception as e:
        print("CRASH DETECTED:")
        traceback.print_exc()

if __name__ == '__main__':
    # User mentioned ID 60 in the log
    debug_crash(60)
