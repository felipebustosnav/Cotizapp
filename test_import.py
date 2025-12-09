
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cotizapp.settings')
django.setup()

try:
    from usuarios.views_auth import RegisterCompanyView
    print("Import SUCCESS: RegisterCompanyView found")
except Exception as e:
    print(f"Import FAILED: {e}")

try:
    from usuarios import urls
    print("URLs Module Loaded")
    print(urls.urlpatterns)
except Exception as e:
    print(f"URLs Load FAILED: {e}")
