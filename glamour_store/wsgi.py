"""
WSGI config for glamour_store project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')

application = get_wsgi_application()

# Run migrations automatically on Vercel startup
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print(f"Migration error: {e}")

app = application
