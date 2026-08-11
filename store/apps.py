from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        import store.signals
        try:
            from django.conf import settings
            from allauth.socialaccount.models import SocialApp
            from django.contrib.sites.models import Site
            
            google_config = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {}).get('google', {}).get('APP', {})
            client_id = google_config.get('client_id')
            secret = google_config.get('secret')
            
            if client_id and secret:
                app, _ = SocialApp.objects.update_or_create(
                    provider='google',
                    defaults={
                        'name': 'Google',
                        'client_id': client_id,
                        'secret': secret,
                    }
                )
                current_site = Site.objects.get_current()
                if current_site and current_site not in app.sites.all():
                    app.sites.add(current_site)
        except Exception:
            pass
