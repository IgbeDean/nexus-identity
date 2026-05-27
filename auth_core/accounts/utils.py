from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(request, user):
    # Force Django to drop the cached version and pull the fresh token from the DB
    user.profile.refresh_from_db()
    
    token = user.profile.verification_token
    verify_url = request.build_absolute_uri(reverse('verify_email', kwargs={'token': token}))
    
    subject = "Action Required: Verify Your Nexus Identity"
    
    # We'll create a simple HTML string here, or you could use a template file
    html_content = f"""
    <div style="background-color: #0a0a0a; color: white; padding: 40px; font-family: sans-serif;">
        <h1 style="color: #3498db;">NEXUS<span>.</span></h1>
        <p>A new identity has been requested for <strong>{user.email}</strong>.</p>
        <p>To finalize your entry into the engine, please click the button below:</p>
        <a href="{verify_url}" style="background: #3498db; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">Verify Identity</a>
        <p style="font-size: 0.8rem; opacity: 0.6;">Link expires in 24 hours.</p>
    </div>
    """
    text_content = strip_tags(html_content) # Fallback for old email clients

    email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()