from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ensure existing social logins have an active user account
        if sociallogin.is_existing:
            if sociallogin.user and not sociallogin.user.is_active:
                sociallogin.user.is_active = True
                sociallogin.user.is_email_verified = True
                sociallogin.user.save(update_fields=['is_active', 'is_email_verified'])
            return

        if not sociallogin.user.email:
            return

        # Check if user with this email address already exists.
        try:
            User = get_user_model()
            user = User.objects.get(email__iexact=sociallogin.user.email)
            
            # Google verification automatically activates and verifies email
            if not user.is_active:
                user.is_active = True
                user.is_email_verified = True
                user.save(update_fields=['is_active', 'is_email_verified'])

            # Connect the social login to the existing user automatically
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if user and not user.is_active:
            user.is_active = True
            user.is_email_verified = True
            user.save(update_fields=['is_active', 'is_email_verified'])
        return user
