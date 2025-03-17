from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from users.models import EndUser
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

class UpdateProfileViewTest(TestCase):

    def setUp(self):
        """Set up a test user and profile."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Test@1234"
        )
        self.end_user = EndUser.objects.create(
            user=self.user,
            phone_number="+123456789",
            age=25,
            gender="male",
            ethnicity="asian",
            last_time_to_work="1_month",
            sector="it"
        )
        self.client.force_login(self.user)
        self.update_profile_url = reverse("update_profile")

    def test_authenticated_user_access(self):
        """Ensure authenticated users can access the profile update page."""
        response = self.client.get(self.update_profile_url)
        self.assertEqual(response.status_code, 200)

    def test_successful_profile_update(self):
        """Test updating the profile with valid data."""
        data = {
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "+987654321",
        }
        response = self.client.post(self.update_profile_url, data, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.end_user.phone_number, "+987654321")

    @patch("users.views.send_mail")
    def test_email_change_triggers_verification(self, mock_send_mail):
        """Test that changing email does not update immediately but triggers verification."""
        data = {"new_email": "newemail@example.com"}
        response = self.client.post(self.update_profile_url, data, follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "test@example.com")  # Email should not change yet
        self.assertEqual(self.user.new_email, "newemail@example.com")  # new_email should be set
        self.assertTrue(mock_send_mail.called)
        self.assertEqual(len(mail.outbox), 1)  # Ensure an email was sent
        session = self.client.session
        self.assertEqual(session.get('profile_update_popup'), 'verification_sent')

    def test_password_change(self):
        """Test changing the password."""
        data = {"new_password": "NewSecurePassword123"}
        response = self.client.post(self.update_profile_url, data, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecurePassword123"))

    def test_invalid_data_shows_error(self):
        """Test submitting invalid data (empty fields)."""
        data = {"first_name": "", "last_name": ""}
        response = self.client.post(self.update_profile_url, data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("There were errors in the form." in str(m) for m in messages))

    def test_unauthenticated_user_redirect(self):
        """Ensure unauthenticated users cannot access update profile."""
        self.client.logout()
        response = self.client.get(self.update_profile_url)
        self.assertRedirects(response, f"/log_in/?next={self.update_profile_url}")
