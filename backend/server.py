"""
ASGI adapter for Django app
This file adapts the Django application to be compatible with the uvicorn setup
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "analyticore_api.settings")

import django
django.setup()

from analyticore_api.asgi import application as app

# Export for uvicorn
__all__ = ['app']
