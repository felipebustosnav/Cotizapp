import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from cotizaciones.models import Cotizacion
from cotizaciones.utils.pdf_generator import generar_pdf_cotizacion
import traceback

def test_pdf_gen():
    try:
        # Get latest quotation
        cotizacion = Cotizacion.objects.last()
        if not cotizacion:
            print("No quotations found.")
            return

        print(f"Testing PDF generation for Cotizacion {cotizacion.numero} (ID: {cotizacion.id})")
        
        pdf = generar_pdf_cotizacion(cotizacion)
        print(f"Success! PDF size: {len(pdf)} bytes")
        
    except Exception as e:
        print("FAILED to generate PDF:")
        traceback.print_exc()

if __name__ == '__main__':
    test_pdf_gen()
