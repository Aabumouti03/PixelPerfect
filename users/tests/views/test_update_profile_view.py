from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core import mail
from users.models import EndUser
from unittest.mock import patch
from django.utils.http import urlsafe_base64_encode
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
            "username": "newuser123",
            "phone_number": "+987654321",
            "age": 30,
            "gender": "female",
            "last_time_to_work": "3_months",
            "sector": "finance",
        }
        response = self.client.post(self.update_profile_url, data, follow=True)
        
        # Refresh from DB to get latest changes
        self.user.refresh_from_db()
        self.end_user.refresh_from_db() 

        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.username, "newuser123")
        self.assertEqual(self.end_user.phone_number, "+987654321") 
        self.assertEqual(self.end_user.age, 30)


    @patch("users.views.send_mail", return_value=1)  #  Simulate that an email was sent
    def test_email_change_triggers_verification(self, mock_send_mail):
        """Test that changing email does not update immediately but triggers verification."""
        data = {
            "new_email": "newemail@example.com",
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "phone_number": "+123456789",
            "age": 25,
            "gender": "male",
            "last_time_to_work": "1_month",
            "sector": "it",
        }
        response = self.client.post(self.update_profile_url, data, follow=True)

        # Refresh user from DB
        self.user.refresh_from_db()
        
        self.assertEqual(self.user.email, "test@example.com")  # Email should not change yet
        self.assertEqual(self.user.new_email, "newemail@example.com")  # new_email should be set
        self.assertTrue(mock_send_mail.called)

        #  Check if an email was actually sent
        self.assertEqual(mock_send_mail.call_count, 1, "Expected send_mail to be called once but wasn't")


    def test_email_not_changed_does_not_trigger_verification(self):
        """Test that submitting the same email does not trigger verification."""
        data = {
            "new_email": "test@example.com",  # Same as current email!
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "phone_number": "+123456789",
            "age": 25,
            "gender": "male",
            "last_time_to_work": "1_month",
            "sector": "it",
        }

        response = self.client.post(self.update_profile_url, data, follow=True)

        # Refresh user from DB
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, "test@example.com")  # Email remains the same
        self.assertIsNone(self.user.new_email)  # new_email should not be set
        self.assertFalse(mail.outbox)  # No email should be sent


    def test_password_change(self):
        """Test changing the password."""
        data = {
            "new_password": "NewSecurePassword123",
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "phone_number": "+123456789",
            "age": 25,
            "gender": "male",
            "last_time_to_work": "1_month",
            "sector": "it",
        }
        response = self.client.post(self.update_profile_url, data, follow=True)
        
        # Refresh user from DB
        self.user.refresh_from_db()
        
        self.assertTrue(self.user.check_password("NewSecurePassword123"))  


    def test_invalid_data_shows_error(self):
        """Test submitting invalid data (empty fields)."""
        data = {
            "first_name": "",
            "last_name": "",
            "username": "",
            "phone_number": "",
            "age": "",
            "gender": "",
            "last_time_to_work": "",
            "sector": "",
        }
        response = self.client.post(self.update_profile_url, data, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("There were errors in the form." in str(m) for m in messages))


    def test_unauthenticated_user_redirect(self):
        """Ensure unauthenticated users cannot access update profile."""
        self.client.logout()
        response = self.client.get(self.update_profile_url)
        self.assertRedirects(response, f"/log_in/?next={self.update_profile_url}")

    def test_user_without_profile_redirects_to_welcome(self):
        """Test that a user without a profile is redirected with an error message."""
        # Create a user without creating an EndUser profile
        user_without_profile = User.objects.create_user(
            username="noprofileuser",
            email="noprofile@example.com",
            password="Test@1234"
        )
        self.client.force_login(user_without_profile)

        response = self.client.get(self.update_profile_url, follow=True)
        
        # Check redirection
        self.assertRedirects(response, reverse('welcome_page'))

        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Profile not found." in str(m) for m in messages))
