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
    
    This link is valid for a limited time and can only be used once. If you do not complete verification, your account may remain inactive.

    If you did not sign up for a ReWork account, you can safely ignore this message.

    We are excited to support your journey toward returning to work with confidence. After verifying your email, you'll be able to:

    • Access our full suite of tailored support modules  
    • Track your readiness progress  
    • Connect with programs designed for your needs  

    If you have any questions or run into issues, feel free to reach out to our support team in the contact us section.

    We hope you enjoy your jouney.

    Best regards,  
    The ReWork Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])