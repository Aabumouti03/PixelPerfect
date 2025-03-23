import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from client.models import Exercise, ExerciseQuestion

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ExerciseModelTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.question_with_blank = ExerciseQuestion.objects.create(
            question_text="Fill in the blank",
            has_blank=True,
            text_before_blank="Start",
            text_after_blank="End"
        )
        self.question_without_blank = ExerciseQuestion.objects.create(
            question_text="What is your name?",
            has_blank=False
        )

    def test_str_with_explicit_type(self):
        exercise = Exercise.objects.create(title="Test Exercise", exercise_type="short_answer")
        expected = "Test Exercise (short_answer)"
        self.assertEqual(str(exercise), expected)

    def test_auto_set_exercise_type_fill_blank(self):
        exercise = Exercise(title="Blank Exercise", exercise_type='')
        models.Model.save(exercise, force_insert=True) 
        exercise.questions.add(self.question_with_blank)
        exercise.save()
        self.assertEqual(exercise.exercise_type, "fill_blank")

    def test_auto_set_exercise_type_short_answer(self):
        exercise = Exercise(title="Non-blank Exercise", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.questions.add(self.question_without_blank)
        exercise.save()
        self.assertEqual(exercise.exercise_type, "short_answer")

    def test_pdf_file_optional(self):
        exercise = Exercise.objects.create(title="No PDF Exercise", exercise_type="short_answer")
        self.assertFalse(exercise.pdf_file)

    def test_pdf_file_upload(self):
        """Test that uploading a PDF file sets the pdf_file field."""
        pdf_content = b"%PDF-1.4 dummy pdf content"
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        exercise = Exercise.objects.create(title="PDF Exercise", exercise_type="short_answer", pdf_file=pdf_file)
        self.assertIsNotNone(exercise.pdf_file.name)
        self.assertTrue(exercise.pdf_file.name.endswith(".pdf"))

    def test_status_default(self):
        exercise = Exercise.objects.create(title="Status Default Exercise", exercise_type="short_answer")
        self.assertEqual(exercise.status, "not_started")

    def test_set_status_valid(self):
        exercise = Exercise.objects.create(
            title="Completed Exercise", exercise_type="short_answer", status="completed"
        )
        self.assertEqual(exercise.status, "completed")

    def test_exercise_with_provided_type(self):
        exercise = Exercise(title="Provided Type Exercise", exercise_type="custom")
        models.Model.save(exercise, force_insert=True)
        exercise.questions.add(self.question_with_blank)
        exercise.save()
        self.assertEqual(exercise.exercise_type, "custom")

    def test_multiple_questions_auto_set(self):
        exercise = Exercise(title="Multiple Questions", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.questions.set([self.question_without_blank, self.question_with_blank])
        exercise.save()
        self.assertEqual(exercise.exercise_type, "fill_blank")

    def test_add_remove_questions(self):
        exercise = Exercise(title="Add Remove Questions", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.questions.add(self.question_with_blank)
        exercise.save()
        initial_type = exercise.exercise_type
        exercise.questions.clear()
        exercise.save()
        self.assertEqual(exercise.exercise_type, initial_type)

    def test_save_without_questions(self):
        exercise = Exercise(title="No Questions Exercise", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.save()
        self.assertEqual(exercise.exercise_type, '')

    def test_update_exercise_after_adding_question(self):
        exercise = Exercise(title="Update After Adding", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.save() 
        self.assertEqual(exercise.exercise_type, '')
        exercise.questions.add(self.question_with_blank)
        exercise.save()
        self.assertEqual(exercise.exercise_type, "fill_blank")

    def test_exercise_str_with_no_exercise_type(self):
        exercise = Exercise(title="Empty Type Exercise", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        expected = "Empty Type Exercise ()"
        self.assertEqual(str(exercise), expected)

    def test_auto_set_priority_multiple_questions(self):
        exercise = Exercise(title="Priority Test", exercise_type='')
        models.Model.save(exercise, force_insert=True)
        exercise.questions.set([self.question_without_blank, self.question_with_blank])
        exercise.save()
        self.assertEqual(exercise.exercise_type, "fill_blank")

    def test_auto_set_does_not_override_provided_type(self):
        exercise = Exercise(title="Do Not Override", exercise_type="custom")
        models.Model.save(exercise, force_insert=True)
        exercise.questions.add(self.question_with_blank)
        exercise.save()
        self.assertEqual(exercise.exercise_type, "custom")
