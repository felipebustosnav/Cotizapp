import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

from cotizaciones.models import Cotizacion

print("Regenerando UUIDs únicos para todas las cotizaciones...")

cotizaciones = Cotizacion.objects.all()
total = cotizaciones.count()

for i, cotizacion in enumerate(cotizaciones, 1):
    # Generar un nuevo UUID único
    cotizacion.uuid = uuid.uuid4()
    cotizacion.save(update_fields=['uuid'])
    print(f"Procesado {i}/{total}: Cotización #{cotizacion.numero}")

print(f"\n✅ Se regeneraron {total} UUIDs exitosamente.")
print("Ahora puedes ejecutar: python manage.py migrate")
