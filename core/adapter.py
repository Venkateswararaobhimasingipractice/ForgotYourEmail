from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class NoNewUsersAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if not user.email:
            # No email, cannot match, so allow creating a new user
            return

        User = get_user_model()

        # 1. Try to match with main email
        try:
            existing_user = User.objects.get(email=user.email)
            sociallogin.connect(request, existing_user)
            return
        except User.DoesNotExist:
            pass

        # 2. Try to match with any of the GitHub emails
        extra_data = sociallogin.account.extra_data
        emails = []

        if 'emails' in extra_data:
            # Only consider verified emails
            emails = [email_entry.get('email') for email_entry in extra_data['emails'] if email_entry.get('verified')]
        print(f"Emails from GitHub: {emails}")
        print(f"User email: {extra_data }")
        for email in emails:
            if not email:
                continue
            try:
                existing_user = User.objects.get(email=email)
                sociallogin.connect(request, existing_user)
                return
            except User.DoesNotExist:
                continue

        # 3. No matching user found
        # → Allow Django to create a NEW user account
        return

