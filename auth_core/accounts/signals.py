from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # create the profile
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()



# signal for when the user is logged in
from django.contrib import messages
from allauth.account.signals import user_logged_in

@receiver(user_logged_in)
def customize_login_message(request, user, **kwargs):
    # If the user has a profile with a name, use it; otherwise, use email
    name = user.profile.full_name().strip()
    welcome_name = name if name else user.email
    
    messages.success(request, f"Identity Verified. Welcome back, {welcome_name}.")