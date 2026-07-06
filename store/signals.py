from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, CountrySetting

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Auto-creates UserProfile for new users to avoid profile lookup errors.
    """
    if created:
        default_country = CountrySetting.objects.first()
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'country': default_country,
                'preferred_language': 'en'
            }
        )
