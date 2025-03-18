from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse

def send_verification_email_after_sign_up(user, request):
    """Send a verification email to new users after sign-up."""
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verification_url = request.build_absolute_uri(
        reverse('verify_email_after_sign_up', kwargs={'uidb64': uidb64, 'token': token})
    )

    subject = "Verify Your Email Address"
    message = f"""
    Hello {user.full_name()},
    
    Thank you for signing up! Please click the link below to verify your email address:
    
    {verification_url}
    
    If you did not sign up for this account, please ignore this email.
    
    Thank you,
    ReWork Team.
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])