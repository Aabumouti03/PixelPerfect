from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from users.models import User, JournalEntry
from datetime import timedelta

class JournalViewTest(TestCase):
    """Test suite for journal_view."""

    def setUp(self):
        """Create a test user and log in."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        login_success = self.client.login(username="testuser", password="testpass")
        
        self.today = now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)

    def test_journal_view_no_date(self):
        """Test accessing the journal view with no date provided."""
        
        response = self.client.get(reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, self.today.strftime("%Y-%m-%d"))

    def test_journal_view_ajax_no_entry(self):
        """Test AJAX request when no journal entry exists for the date."""
        
        response = self.client.get(
            reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"success": False, "error": "No entry found."})

    def test_journal_view_ajax_with_entry(self):
        """Test AJAX request when a journal entry exists for the date."""
        
        journal_entry = JournalEntry.objects.create(
            user=self.user, date=self.today, sleep_hours=7, caffeine="yes"
        )
        
        
        response = self.client.get(
            reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        

        
        self.assertEqual(response.status_code, 200)
        self.assertIn("sleep_hours", response.json()["data"])
        self.assertIn("caffeine", response.json()["data"])
        
        expected_response = {
            "success": True,
            "data": {
                "sleep_hours": 7,
                "caffeine": "yes",
                "hydration": None,
                "stress": None,
                "goal_progress": None,
                "notes": None,
                "connected_with_family": None,
                "expressed_gratitude": None,
                "outdoors": None,
                "sunset": None,
            }
        }
        
        
        self.assertJSONEqual(response.content, expected_response)
