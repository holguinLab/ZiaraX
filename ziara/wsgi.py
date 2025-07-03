"""
WSGI config for ziara project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Detectar BASE_DIR dinámicamente
BASE_DIR = Path(__file__).resolve().parent.parent

# Agregar la ruta raíz del proyecto a sys.path
sys.path.append(str(BASE_DIR))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ziara.settings')
application = get_wsgi_application()
