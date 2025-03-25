from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

class SaveJournalEntryTest(TestCase):
    """Test case for save_journal_entry view"""

    def setUp(self):
        """Setup test user and client"""
        self.client = Client()
        self.user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.url = reverse("save_journal_entry")  # Ensure this matches the name in your `urls.py`

    def test_create_new_journal_entry(self):
        """Test creating a new journal entry"""
        payload = {"date": "2025-03-15", "sleep_hours": 7, "caffeine": "yes", "hydration": 8}

        response = self.client.post(
            self.url,
            json.dumps(payload),
            content_type="application/json"
        )
        


        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, {"success": True, "message": "Journal entry saved."})

    def test_invalid_date_format(self):
        """Test handling of invalid date format"""
        payload = {"date": "15-03-2025"}  # Invalid format

        response = self.client.post(
            self.url,
            json.dumps(payload),
            content_type="application/json"
        )



        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid date format. Use YYYY-MM-DD."})

    def test_missing_date_field(self):
        """Test handling of missing date field"""
        payload = {"sleep_hours": 6}  # Missing date

        response = self.client.post(
            self.url,
            json.dumps(payload),
            content_type="application/json"
        )
        


        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Date is required."})

    def test_invalid_request_method(self):
        """Test handling of invalid request methods"""

        response = self.client.get(self.url)
        


        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request method."})

    def test_invalid_json_format(self):
        """Test handling of invalid JSON format"""

        response = self.client.post(
            self.url,
            data="This is not a valid JSON",  # Intentionally wrong format
            content_type="application/json"
        )
        


        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid JSON format."})
