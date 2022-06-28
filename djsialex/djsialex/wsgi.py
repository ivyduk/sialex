"""
WSGI config for djsialex project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# dev
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djsialex.djsialex.settings')

application = get_wsgi_application()
