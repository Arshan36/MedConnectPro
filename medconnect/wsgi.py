"""
WSGI config for medconnect project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medconnect.settings')

application = get_wsgi_application()

# For Vercel deployment
app = application
