from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class EmailVerificationViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )

    def test_sign_up_email_verification_view(self):
        """Should load the email sent confirmation page."""
        response = self.client.get(reverse('sign_up_email_verification'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/sign_up_email_verification.html')

    def test_verification_done_view(self):
        """Should load the success page after email is verified."""
        response = self.client.get(reverse('verification_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/verification_done.html')

    def test_verify_email_success(self):
        """Should verify email if the UID and token are correct."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.get(reverse('verify_email_after_sign_up', kwargs={'uidb64': uidb64, 'token': token}))
        self.assertRedirects(response, reverse('verification_done'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_verify_email_invalid_uid(self):
        """Should fail gracefully if the UID is invalid."""
        response = self.client.get(reverse('verify_email_after_sign_up', kwargs={'uidb64': 'invalid', 'token': 'token'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/invalid_verification.html')

    def test_verify_email_invalid_token(self):
        """Should show error page if the token is invalid or expired."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        fake_token = 'wrong-token'
        response = self.client.get(reverse('verify_email_after_sign_up', kwargs={'uidb64': uidb64, 'token': fake_token}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/invalid_verification.html')
