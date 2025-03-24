from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import Questionnaire
import datetime

class QuestionnaireModelTest(TestCase):
    def test_str_and_created_at(self):
        
        questionnaire = Questionnaire.objects.create(
            title="Customer Satisfaction Survey",
            description="A survey about customer satisfaction."
        )
        self.assertEqual(str(questionnaire), "Customer Satisfaction Survey")
        self.assertEqual(questionnaire.created_at, datetime.date.today())

    def test_is_active_default(self):
        """Test that is_active defaults to False when not provided."""
        questionnaire = Questionnaire.objects.create(
            title="Feedback Form",
            description="Feedback without active flag."
        )
        self.assertFalse(questionnaire.is_active)

    def test_set_is_active_true(self):
        """Test that is_active can be set to True on creation."""
        questionnaire = Questionnaire.objects.create(
            title="Active Survey",
            description="This survey is active.",
            is_active=True
        )
        self.assertTrue(questionnaire.is_active)

    def test_description_blank(self):
        """Test that the description field can be left blank and defaults to an empty string."""
        questionnaire = Questionnaire.objects.create(
            title="No Description Survey"
        )
        self.assertEqual(questionnaire.description, "")

    def test_created_at_immutable(self):
        """Test that the created_at field remains unchanged after updating other fields."""
        questionnaire = Questionnaire.objects.create(
            title="Immutable Test",
            description="Testing created_at immutability."
        )
        created_at_original = questionnaire.created_at
        questionnaire.title = "Updated Title"
        questionnaire.save()
        self.assertEqual(questionnaire.created_at, created_at_original)

    def test_multiple_questionnaires(self):
        """Test that multiple Questionnaire instances can be created and retrieved."""
        q1 = Questionnaire.objects.create(
            title="Survey 1",
            description="First survey."
        )
        q2 = Questionnaire.objects.create(
            title="Survey 2",
            description="Second survey."
        )
        questionnaires = Questionnaire.objects.all()
        self.assertEqual(questionnaires.count(), 2)
        titles = {q.title for q in questionnaires}
        self.assertSetEqual(titles, {"Survey 1", "Survey 2"})

    def test_title_length_validation(self):
        """Test that a title exceeding 200 characters raises a ValidationError."""
        long_title = "a" * 201 
        questionnaire = Questionnaire(
            title=long_title,
            description="Testing long title."
        )
        with self.assertRaises(ValidationError):
            questionnaire.full_clean()

    def test_missing_title_validation(self):
        """Test that a missing (empty) title raises a ValidationError on full_clean."""
        questionnaire = Questionnaire(
            title="",
            description="Missing title test."
        )
        with self.assertRaises(ValidationError):
            questionnaire.full_clean()

    def test_whitespace_title(self):
        """Test that a title with leading/trailing whitespace is stored as provided."""
        title = "  Whitespace Title  "
        questionnaire = Questionnaire.objects.create(
            title=title,
            description="Testing whitespace."
        )
        self.assertEqual(questionnaire.title, title)

    def test_update_description(self):
        """Test that updating the description field works as expected."""
        questionnaire = Questionnaire.objects.create(
            title="Update Test",
            description="Initial description."
        )
        questionnaire.description = "Updated description."
        questionnaire.save()
        questionnaire.refresh_from_db()
        self.assertEqual(questionnaire.description, "Updated description.")
