import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "license_service.settings.prod")

application = get_asgi_application()
