from django.test import TestCase
from django.utils import timezone
from users.models import EndUser
from users.models import StickyNote
from django.contrib.auth import get_user_model

User = get_user_model()

class StickyNoteModelTest(TestCase):
    """Test suite for the StickyNote model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.end_user = EndUser.objects.create(user=self.user, age=25, gender="male", sector="education")
    
    def test_create_sticky_note(self):
        """Test creating a StickyNote and checking its string representation."""
        sticky_note = StickyNote.objects.create(
            user=self.end_user,
            content="This is a test sticky note."
        )

        self.assertEqual(sticky_note.user, self.end_user)
        self.assertEqual(sticky_note.content, "This is a test sticky note.")
        self.assertEqual(str(sticky_note), f"StickyNote by {self.user.username}")

    def test_created_at_and_updated_at_fields(self):
        """Test automatic handling of created_at and updated_at fields."""
        sticky_note = StickyNote.objects.create(
            user=self.end_user,
            content="Testing created_at and updated_at fields."
        )
        
        self.assertIsNotNone(sticky_note.created_at)
        self.assertIsNotNone(sticky_note.updated_at)
        self.assertAlmostEqual(sticky_note.created_at, sticky_note.updated_at, delta=timezone.timedelta(seconds=1))

    def test_updated_at_field_changes_on_update(self):
        """Test that updating a StickyNote changes the updated_at field."""
        sticky_note = StickyNote.objects.create(
            user=self.end_user,
            content="Initial content."
        )
        
        original_updated_at = sticky_note.updated_at

        sticky_note.content = "Updated content."
        sticky_note.save()

        sticky_note.refresh_from_db()

        self.assertNotEqual(sticky_note.updated_at, original_updated_at)
        self.assertTrue(sticky_note.updated_at > original_updated_at)

    def test_delete_user_deletes_sticky_notes(self):
        """Test that deleting an EndUser deletes all related StickyNotes."""
        sticky_note1 = StickyNote.objects.create(user=self.end_user, content="Note 1")
        sticky_note2 = StickyNote.objects.create(user=self.end_user, content="Note 2")
        
        self.assertEqual(StickyNote.objects.filter(user=self.end_user).count(), 2)

        sticky_notes_user_id = self.end_user.id

        self.end_user.delete()
        
        self.assertEqual(StickyNote.objects.filter(user_id=sticky_notes_user_id).count(), 0)
