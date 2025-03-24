from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from users.models import JournalEntry

User = get_user_model()

class JournalEntryModelTest(TestCase):
    """Test suite for the JournalEntry model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_create_journal_entry(self):
        """Test creating a JournalEntry and checking its string representation."""
        journal_entry = JournalEntry.objects.create(
            user=self.user,
            date=now().date(),
            connected_with_family="yes",
            expressed_gratitude="yes",
            caffeine="no",
            hydration=5,
            goal_progress="moderate",
            outdoors="yes",
            sunset="no",
            stress="medium",
            sleep_hours=7,
            notes="Felt productive and calm today."
        )
        
        self.assertEqual(str(journal_entry), f"{self.user.username} - {journal_entry.date}")
        self.assertEqual(journal_entry.user, self.user)
        self.assertEqual(journal_entry.connected_with_family, "yes")
        self.assertEqual(journal_entry.expressed_gratitude, "yes")
        self.assertEqual(journal_entry.caffeine, "no")
        self.assertEqual(journal_entry.hydration, 5)
        self.assertEqual(journal_entry.goal_progress, "moderate")
        self.assertEqual(journal_entry.outdoors, "yes")
        self.assertEqual(journal_entry.sunset, "no")
        self.assertEqual(journal_entry.stress, "medium")
        self.assertEqual(journal_entry.sleep_hours, 7)
        self.assertEqual(journal_entry.notes, "Felt productive and calm today.")

    def test_unique_together_constraint(self):
        """Test that a user cannot have multiple journal entries for the same date."""
        JournalEntry.objects.create(user=self.user, date=now().date())
        
        with self.assertRaises(Exception):
            JournalEntry.objects.create(user=self.user, date=now().date())

    def test_journal_entry_with_null_fields(self):
        """Test creating a JournalEntry with optional fields left blank or null."""
        journal_entry = JournalEntry.objects.create(
            user=self.user,
            date=now().date(),
            connected_with_family=None,
            expressed_gratitude=None,
            caffeine=None,
            hydration=None,
            goal_progress=None,
            outdoors=None,
            sunset=None,
            stress=None,
            sleep_hours=None,
            notes=None
        )
        
        self.assertEqual(journal_entry.connected_with_family, None)
        self.assertEqual(journal_entry.expressed_gratitude, None)
        self.assertEqual(journal_entry.caffeine, None)
        self.assertEqual(journal_entry.hydration, None)
        self.assertEqual(journal_entry.goal_progress, None)
        self.assertEqual(journal_entry.outdoors, None)
        self.assertEqual(journal_entry.sunset, None)
        self.assertEqual(journal_entry.stress, None)
        self.assertEqual(journal_entry.sleep_hours, None)
        self.assertEqual(journal_entry.notes, None)

    def test_journal_entry_str_method(self):
        """Test the __str__() method of JournalEntry."""
        journal_entry = JournalEntry.objects.create(user=self.user, date=now().date())
        self.assertEqual(str(journal_entry), f"{self.user.username} - {journal_entry.date}")
