from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, StickyNote
import json
from django.conf import settings

User = get_user_model()

class SaveNotesViewTest(TestCase):
    def setUp(self):
        """Set up test data before running each test."""
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.end_user = EndUser.objects.create(user=self.user)

        # Define the API endpoint
        self.url = reverse("save_notes")  # Make sure "save_notes" is correctly defined in `urls.py`

    def test_authenticated_user_can_save_note(self):
        """Test that an authenticated user can save a note successfully."""
        self.client.login(username="testuser", password="testpass")

        data = {"content": "This is a test note"}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Check if the note was saved in the database
        sticky_note = StickyNote.objects.get(user=self.end_user)
        self.assertEqual(sticky_note.content, "This is a test note")

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that an unauthenticated user is redirected to the login page."""
        data = {"content": "This is a test note"}
        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 302)  # 302 = Redirect
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # Default login URL

    def test_invalid_request_method_fails(self):
        """Test that only POST requests are allowed."""
        self.client.login(username="testuser", password="testpass")

        response = self.client.get(self.url)  # Sending GET instead of POST
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request method"})
