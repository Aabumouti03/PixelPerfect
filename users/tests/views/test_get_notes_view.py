from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from users.models import EndUser, StickyNote

User = get_user_model()

class GetNotesViewTest(TestCase):
    def setUp(self):
        """Set up test data before running each test."""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.end_user = EndUser.objects.create(user=self.user)

        # Define the API endpoint
        self.url = reverse("get_notes")  # Ensure "get_notes" is defined in `urls.py`

    def test_authenticated_user_can_fetch_notes(self):
        """Test that an authenticated user can fetch their saved sticky note."""
        self.client.login(username="testuser", password="testpass")

        # Create a sticky note for the user
        StickyNote.objects.create(user=self.end_user, content="Test note content")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "content": "Test note content"})

    def test_authenticated_user_with_no_notes_gets_empty_content(self):
        """Test that an authenticated user with no notes receives an empty response."""
        self.client.login(username="testuser", password="testpass")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "content": ""})  # Should return empty string

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)  # 302 = Redirect
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # ✅ Uses Django's actual login URL
