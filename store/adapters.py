import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if user.email:
            user.username = user.email
            user.is_active = True
            user.is_email_verified = True
        return user

    def pre_social_login(self, request, sociallogin):
        # 1. Existing social account login
        if sociallogin.is_existing:
            if sociallogin.user:
                if not sociallogin.user.is_active or not sociallogin.user.is_email_verified:
                    sociallogin.user.is_active = True
                    sociallogin.user.is_email_verified = True
                    sociallogin.user.save(update_fields=['is_active', 'is_email_verified'])
            return

        email = sociallogin.user.email or sociallogin.account.extra_data.get('email')
        if not email:
            return

        # 2. Existing user by email -> connect social account safely
        User = get_user_model()
        try:
            existing_user = User.objects.get(email__iexact=email)
            if not existing_user.is_active or not existing_user.is_email_verified:
                existing_user.is_active = True
                existing_user.is_email_verified = True
                existing_user.save(update_fields=['is_active', 'is_email_verified'])
            
            # Safely connect without raising AlreadyConnected exceptions
            try:
                sociallogin.connect(request, existing_user)
            except Exception as conn_err:
                logger.info(f"Sociallogin auto-connect note: {conn_err}")
                sociallogin.user = existing_user
        except User.DoesNotExist:
            # 3. New user signup via Google
            sociallogin.user.username = email
            sociallogin.user.email = email
            sociallogin.user.is_active = True
            sociallogin.user.is_email_verified = True

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        if user:
            if not user.username and user.email:
                user.username = user.email
            user.is_active = True
            user.is_email_verified = True

        try:
            saved_user = super().save_user(request, sociallogin, form)
        except Exception as e:
            logger.error(f"Error in super().save_user: {e}")
            User = get_user_model()
            saved_user = User.objects.filter(email__iexact=user.email).first()
            if not saved_user:
                saved_user = user
                saved_user.save()

        if saved_user:
            if not saved_user.username and saved_user.email:
                saved_user.username = saved_user.email
            saved_user.is_active = True
            saved_user.is_email_verified = True
            saved_user.save()

        return saved_user
