import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from client.models import Section, Exercise

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SectionModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_str_without_diagram(self):
        section = Section.objects.create(title="Test Section")
        expected = "Test Section (Diagram: No)"
        self.assertEqual(str(section), expected)

    def test_str_with_diagram(self):
        image_content = b"dummyimagecontent"
        image_file = SimpleUploadedFile("test.jpg", image_content, content_type="image/jpeg")
        section = Section.objects.create(title="Test Section 2", diagram=image_file)
        expected = "Test Section 2 (Diagram: Yes)"
        self.assertEqual(str(section), expected)

    def test_unique_title_constraint(self):
        Section.objects.create(title="Unique Section")
        with self.assertRaises(Exception):
            Section.objects.create(title="Unique Section")

    def test_default_text_position_from_diagram(self):
        """Test that the default text_position_from_diagram is set to 'below'."""
        section = Section.objects.create(title="Text Position Test")
        self.assertEqual(section.text_position_from_diagram, 'below')

    def test_invalid_text_position_from_diagram(self):
        """Test that an invalid text_position_from_diagram value raises a ValidationError."""
        section = Section(title="Invalid Text Position", text_position_from_diagram="invalid")
        with self.assertRaises(ValidationError):
            section.full_clean()

    def test_description_optional(self):
        """Test that the description field is optional and defaults to None."""
        section = Section.objects.create(title="Optional Description Test")
        self.assertIsNone(section.description)

    def test_add_exercises(self):
        """Test that exercises can be added to the section's many-to-many field."""
        section = Section.objects.create(title="Section with Exercises")
        exercise = Exercise.objects.create(title="Exercise 1")
        section.exercises.add(exercise)
        self.assertIn(exercise, section.exercises.all())

    def test_multiple_exercises(self):
        """Test that multiple exercises can be assigned to a section."""
        section = Section.objects.create(title="Multiple Exercises Test")
        exercise1 = Exercise.objects.create(title="Exercise A")
        exercise2 = Exercise.objects.create(title="Exercise B")
        section.exercises.set([exercise1, exercise2])
        self.assertEqual(section.exercises.count(), 2)
        exercises_titles = [ex.title for ex in section.exercises.all()]
        self.assertCountEqual(exercises_titles, ["Exercise A", "Exercise B"])

    def test_custom_text_position_from_diagram(self):
        """Test that setting a valid custom text_position_from_diagram works correctly.
        (Assuming 'above' is a valid choice in QUESTION_POSITIONS.)"""
        section = Section.objects.create(title="Custom Text Position", text_position_from_diagram="above")
        self.assertEqual(section.text_position_from_diagram, "above")

    def test_exercises_default_empty(self):
        """Test that a new Section has an empty exercises many-to-many relation."""
        section = Section.objects.create(title="Empty Exercises Test")
        self.assertEqual(section.exercises.count(), 0)
