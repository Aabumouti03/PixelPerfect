from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import ExerciseQuestion

class ExerciseQuestionModelTest(TestCase):
    def test_clean_with_blank_missing_fields(self):
        """Test that clean() raises a ValidationError when both blank fields are missing."""
        question = ExerciseQuestion(
            question_text="Fill the gap",
            has_blank=True,
            text_before_blank="",
            text_after_blank=""
        )
        with self.assertRaises(ValidationError):
            question.clean()

    def test_clean_with_blank_one_field(self):
        """Test that clean() passes when at least one blank field is provided (text_before given)."""
        question = ExerciseQuestion(
            question_text="Fill the gap",
            has_blank=True,
            text_before_blank="Start",
            text_after_blank=""
        )
        try:
            question.clean()  
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly when one field was provided!")

    def test_str_with_blank(self):
        """Test __str__ returns the blank format when has_blank is True."""
        question = ExerciseQuestion.objects.create(
            question_text="Fill the gap",
            has_blank=True,
            text_before_blank="Hello",
            text_after_blank="World"
        )
        expected = "Hello ____ World"
        self.assertEqual(str(question), expected)

    def test_str_without_blank(self):
        """Test __str__ returns question_text when has_blank is False."""
        question = ExerciseQuestion.objects.create(
            question_text="Simple question?",
            has_blank=False
        )
        self.assertEqual(str(question), "Simple question?")

    def test_clean_with_blank_both_fields(self):
        """Test that clean() passes when both text_before_blank and text_after_blank are provided."""
        question = ExerciseQuestion(
            question_text="Complete the sentence",
            has_blank=True,
            text_before_blank="Good",
            text_after_blank="Morning"
        )
        try:
            question.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly when both fields were provided!")

    def test_clean_when_not_blank_empty_fields(self):
        """Test that clean() passes when has_blank is False even if blank fields are empty."""
        question = ExerciseQuestion(
            question_text="No blanks needed",
            has_blank=False,
            text_before_blank="",
            text_after_blank=""
        )
        try:
            question.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly when has_blank is False!")

    def test_str_with_non_blank_ignores_blank_fields(self):
        """Test that __str__ returns question_text even if blank fields are provided when has_blank is False."""
        question = ExerciseQuestion.objects.create(
            question_text="Regular question?",
            has_blank=False,
            text_before_blank="Should be ignored",
            text_after_blank="Also ignored"
        )
        self.assertEqual(str(question), "Regular question?")

    def test_question_text_required(self):
        """Test that an empty question_text raises a ValidationError on full_clean()."""
        question = ExerciseQuestion(
            question_text="",
            has_blank=False
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_str_with_whitespace_in_blanks(self):
        """Test that __str__ preserves whitespace in blank fields."""
        question = ExerciseQuestion.objects.create(
            question_text="Fill the gap",
            has_blank=True,
            text_before_blank="  LeadingSpace",
            text_after_blank="TrailingSpace  "
        )
        expected = "  LeadingSpace ____ TrailingSpace  "
        self.assertEqual(str(question), expected)

    def test_clean_with_null_blank_fields(self):
        """Test that clean() raises a ValidationError when both blank fields are None and has_blank is True."""
        question = ExerciseQuestion(
            question_text="Gap test",
            has_blank=True,
            text_before_blank=None,
            text_after_blank=None
        )
        with self.assertRaises(ValidationError):
            question.clean()

    def test_clean_when_not_blank_null_fields(self):
        """Test that clean() passes when has_blank is False even if blank fields are None."""
        question = ExerciseQuestion(
            question_text="No blanks required",
            has_blank=False,
            text_before_blank=None,
            text_after_blank=None
        )
        try:
            question.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for has_blank False with null fields!")

    def test_str_with_null_blank_fields(self):
        """Test __str__ output when has_blank is True and one field is provided while the other is None."""
        question = ExerciseQuestion.objects.create(
            question_text="Incomplete blanks",
            has_blank=True,
            text_before_blank="Provided",
            text_after_blank=None
        )
        expected = "Provided ____ None"
        self.assertEqual(str(question), expected)

    def test_clean_with_blank_only_after(self):
        """Test that clean() passes when only text_after_blank is provided (text_before_blank empty)."""
        question = ExerciseQuestion(
            question_text="Fill the gap after",
            has_blank=True,
            text_before_blank="",
            text_after_blank="End"
        )
        try:
            question.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly when only text_after_blank was provided!")
