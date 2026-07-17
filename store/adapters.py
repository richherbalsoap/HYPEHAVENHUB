from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just for new social connections
        if sociallogin.is_existing:
            return

        # Some social logins don't have an email address
        if not sociallogin.user.email:
            return

        # Check if given email address already exists.
        try:
            User = get_user_model()
            user = User.objects.get(email__iexact=sociallogin.user.email)
            
            # Connect the social login to the existing user automatically
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
