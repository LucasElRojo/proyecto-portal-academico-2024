import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_app.settings")  # Cambia a tu archivo de configuración

app = get_wsgi_application()