from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from users.models import User, JournalEntry
from datetime import timedelta

class JournalViewTest(TestCase):
    """Test suite for journal_view."""

    def setUp(self):
        """Create a test user and login."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.today = now().date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)

    def test_journal_view_without_entry(self):
        """Test that a journal page with no entry renders an empty form."""
        response = self.client.get(reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Daily Journal")  # Ensure the page title is present
        self.assertContains(response, 'name="sleep_hours"')  # Check if sleep_hours input exists
        self.assertContains(response, 'name="caffeine"')  # Ensure caffeine input exists
        self.assertContains(response, 'name="hydration"')  # Ensure hydration input exists


    def test_journal_view_with_existing_entry(self):
        """Test that a journal page with an existing entry shows saved data."""
        JournalEntry.objects.create(
            user=self.user, date=self.today, sleep_hours=7, caffeine="yes",
            hydration=8, stress="medium", goal_progress="high", notes="Had a great day!"
        )
        response = self.client.get(reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "value=\"7\"")  # Check if sleep hours are displayed
        self.assertContains(response, "value=\"yes\"")  # Check if caffeine is pre-selected
        self.assertContains(response, "value=\"8\"")  # Check if hydration is prefilled
        self.assertContains(response, "Had a great day!")  # Check if notes appear

    def test_journal_view_invalid_date(self):
        """Test handling of an invalid date format."""
        response = self.client.get(reverse("journal_by_date", args=["invalid-date"]))
        self.assertEqual(response.status_code, 200)  # Should still render the page
        self.assertContains(response, "Daily Journal")  # Page should load with default date

    def test_previous_and_next_day_navigation(self):
        """Test that the 'Previous' and 'Next' buttons link to the correct dates."""
        response = self.client.get(reverse("journal_by_date", args=[self.today.strftime("%Y-%m-%d")]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"/journal/{self.yesterday.strftime('%Y-%m-%d')}/")  # Previous link
        self.assertContains(response, f"/journal/{self.tomorrow.strftime('%Y-%m-%d')}/")  # Next link
