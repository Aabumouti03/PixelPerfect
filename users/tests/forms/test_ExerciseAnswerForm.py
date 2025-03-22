from django.test import TestCase
from users.forms import ExerciseAnswerForm
from client.models import Exercise, ExerciseQuestion

class ExerciseAnswerFormTest(TestCase):

    def setUp(self):
        """Set up an exercise with questions for testing."""
        self.exercise = Exercise.objects.create(title="Sample Exercise", exercise_type="short_answer")
        self.question1 = ExerciseQuestion.objects.create(
            question_text="What is 2+2?", has_blank=False
        )
        self.question2 = ExerciseQuestion.objects.create(
            question_text="What is the capital of France?", has_blank=False
        )
        self.exercise.questions.add(self.question1, self.question2)

    def test_form_has_correct_fields(self):
        """Ensure the form initializes with the correct fields."""
        form = ExerciseAnswerForm(exercise=self.exercise)

        self.assertIn(f'answer_{self.question1.id}', form.fields)
        self.assertIn(f'answer_{self.question2.id}', form.fields)
        self.assertEqual(form.fields[f'answer_{self.question1.id}'].label, "What is 2+2?")
        self.assertEqual(form.fields[f'answer_{self.question2.id}'].label, "What is the capital of France?")

    def test_valid_form_submission(self):
        """Test form submission with valid data."""
        form_data = {
            f'answer_{self.question1.id}': '4',
            f'answer_{self.question2.id}': 'Paris',
        }
        form = ExerciseAnswerForm(data=form_data, exercise=self.exercise)
        self.assertTrue(form.is_valid())

    def test_invalid_form_submission(self):
        """Test form submission with missing answers."""
        form_data = {
            f'answer_{self.question1.id}': '4',
        }
        form = ExerciseAnswerForm(data=form_data, exercise=self.exercise)
        self.assertFalse(form.is_valid()) 
