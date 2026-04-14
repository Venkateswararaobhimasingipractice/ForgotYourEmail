from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def update_user_profile(sender, request, user, **kwargs):
    if not user.username:
        user.username = user.email.split('@')[0]
        user.save()
