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

# Import allauth signal to detect login
from allauth.account.signals import user_logged_in
from .models import Order

@receiver(user_logged_in)
def merge_guest_orders_on_login(request, user, **kwargs):
    """
    Merge guest orders created with `guest_email` into the user's account upon login.
    """
    if user.email:
        guest_orders = Order.objects.filter(guest_email=user.email).exclude(user=user)
        if guest_orders.exists():
            guest_orders.update(user=user)
