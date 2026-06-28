"""
WSGI config for glamour_store project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glamour_store.settings')

# Auto-migrate, seed data, and create superuser on Vercel cold start
if os.environ.get('VERCEL') or os.environ.get('PGDATABASE'):
    try:
        import django
        django.setup()

        from django.db import connection
        from django.core.management import call_command

        # 1. Run all migrations (creates tables)
        call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)

        # 2. Load initial product/category data if DB is empty (check brand count too)
        with connection.cursor() as cursor:
            needs_seed = False
            try:
                cursor.execute("SELECT COUNT(*) FROM store_product")
                prod_count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM store_brand")
                brand_count = cursor.fetchone()[0]
                if prod_count == 0 or brand_count == 0:
                    needs_seed = True
            except Exception:
                needs_seed = True

            if needs_seed:
                try:
                    call_command('loaddata', 'store/fixtures/initial_data.json', verbosity=0)
                except Exception:
                    pass

        # 3. Create superuser admin if none exists
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@hypehavenhub.com')
            ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'HypeAdmin@2024')
            if not User.objects.filter(is_superuser=True).exists():
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
