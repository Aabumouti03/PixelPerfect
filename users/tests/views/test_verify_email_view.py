from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from users.models import EndUser

User = get_user_model()

class VerifyEmailViewTest(TestCase):

    def setUp(self):
        """Set up a test user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            new_email="newemail@example.com",
            password="Test@1234"
        )
        self.end_user = EndUser.objects.create(user=self.user)

    def generate_verification_url(self):
        """Helper function to generate a valid verification link."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        return reverse("verify_email", kwargs={"uidb64": uid, "token": token})

    def test_successful_email_verification(self):
        """Test verifying email updates the user profile."""
        verification_url = self.generate_verification_url()
        response = self.client.get(verification_url, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")  # Email should now be updated
        self.assertIsNone(self.user.new_email)  # new_email should be cleared
        self.assertTrue(self.user.email_verified)  # Mark email as verified
        session = self.client.session
        self.assertEqual(session.get('profile_update_popup'), 'profile_updated')
        self.assertRedirects(response, reverse("log_in"))

    def test_invalid_verification_link(self):
        """Test invalid verification link does not update email."""
        invalid_uid = urlsafe_base64_encode(force_bytes(99999))  # Using an ID that doesn’t exist
        invalid_url = reverse("verify_email", args=[invalid_uid, "invalid-token"])        
        response = self.client.get(invalid_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")  # Email should not change
        self.assertEqual(response.content.decode(), "Invalid verification link.")

    def test_expired_verification_link(self):
        """Test expired token does not verify email."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        expired_token = "invalidtoken"  # Simulate an expired token
        expired_url = reverse("verify_email", kwargs={"uidb64": uid, "token": expired_token})
        response = self.client.get(expired_url)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")  # Email should not change
        self.assertEqual(response.content.decode(), "Invalid or expired token.")
