from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth import logout
from users.models import EndUser
from django.contrib.messages import get_messages
from unittest.mock import patch


User = get_user_model()

class DeleteAccountViewTest(TestCase):
    def setUp(self):
        """Set up a test user and log them in."""
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
        self.delete_url = reverse("delete_account")
        self.welcome_url = reverse("welcome_page")
        self.profile_url = reverse("profile")


    def test_delete_account_confirmation_page_loads(self):
        """Test that the delete account confirmation page loads correctly."""
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Are you sure you want to delete your account?")


    def test_successful_account_deletion(self):
        """Test that submitting a POST request deletes the user and redirects to the welcome page."""
        response = self.client.post(self.delete_url, follow=True)

        # User should be deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username="testuser")

        # User should be logged out
        self.assertNotIn('_auth_user_id', self.client.session)

        self.assertRedirects(response, self.welcome_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Your account has been successfully deleted.")


    def test_account_deletion_error(self):
        """Simulate an error during account deletion and ensure the user is redirected to profile page."""
        with patch.object(User, "delete", side_effect=Exception("Test deletion error")):
            response = self.client.post(self.delete_url, follow=True)

        self.assertTrue(User.objects.filter(username="testuser").exists())

        self.assertRedirects(response, self.profile_url)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "An error occurred while deleting your account: Test deletion error")
