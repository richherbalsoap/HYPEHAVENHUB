"""
WSGI config for glamour_store project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')

# Auto-migrate and ensure a superuser exists on cold start.
#
# IMPORTANT: this used to also auto-load store/fixtures/initial_data.json
# (demo jhumka box data) whenever the product or brand table was empty.
# That is gone now — on a real persistent Postgres DB, an empty product
# table almost always means "the shop owner deleted everything on
# purpose", not "this is a fresh seed". Auto-restoring demo data in that
# case would silently undo real admin actions. If you ever want the demo
# catalog back, run it explicitly:
#   python manage.py loaddata store/fixtures/initial_data.json
if os.environ.get('VERCEL') or os.environ.get('POSTGRES_URL') or os.environ.get('PGDATABASE'):
    try:
        import django
        django.setup()

        from django.core.management import call_command

        # Run all pending migrations. This is safe/idempotent on a
        # persistent Postgres DB — it only applies migrations that
        # haven't been applied yet, it never deletes or reseeds data.
        call_command('migrate', verbosity=0, interactive=False)

        # Create a superuser ONLY if explicit admin credentials are
        # provided via environment variables AND no superuser exists
        # yet. No hardcoded fallback password — if ADMIN_EMAIL/
        # ADMIN_PASSWORD aren't set, this step is skipped silently so
        # we never create an account with a known/weak password.
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
            ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
            if ADMIN_EMAIL and ADMIN_PASSWORD and not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email=ADMIN_EMAIL,
                    password=ADMIN_PASSWORD,
                )
        except Exception:
            pass

    except Exception as e:
        import sys
        print(f"[WSGI startup] Error: {e}", file=sys.stderr)

application = get_wsgi_application()
app = application
