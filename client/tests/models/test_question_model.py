from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import Questionnaire, Question, Category

class QuestionModelTest(TestCase):
    def setUp(self):
        self.questionnaire = Questionnaire.objects.create(
            title="Product Feedback",
            description="Feedback for our new product."
        )
        self.category = Category.objects.create(name="General")

    def test_str(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="How do you rate our product?",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        # __str__ returns "Questionnaire Title - first 30 characters of question_text"
        self.assertTrue(str(question).startswith("Product Feedback -"))

    def test_default_sentiment(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Do you like our product?",
            question_type="AGREEMENT",
            is_required=True,
            category=self.category
        )
        self.assertEqual(question.sentiment, 1)

    def test_question_type_choices(self):
        question = Question(
            questionnaire=self.questionnaire,
            question_text="Invalid type question",
            question_type="INVALID",
            is_required=True,
            category=self.category
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_is_required_default(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Default required question",
            question_type="RATING",
            category=self.category,
            sentiment=1
        )
        self.assertTrue(question.is_required)

    def test_sentiment_negative(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Negative sentiment question",
            question_type="AGREEMENT",
            is_required=False,
            category=self.category,
            sentiment=-1
        )
        self.assertEqual(question.sentiment, -1)

    def test_str_truncation(self):
        long_text = "This is a very long question text that exceeds thirty characters."
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text=long_text,
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        expected_str = f"{self.questionnaire.title} - {long_text[:30]}"
        self.assertEqual(str(question), expected_str)

    def test_category_set_null_on_delete(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Question with category",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        # Delete the category and refresh the question.
        self.category.delete()
        question.refresh_from_db()
        self.assertIsNone(question.category)

    def test_questionnaire_related_name(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Related question",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        # The related name 'questions' on Questionnaire should include this question.
        self.assertIn(question, self.questionnaire.questions.all())

    def test_question_text_required(self):
        # An empty question_text should raise a ValidationError.
        question = Question(
            questionnaire=self.questionnaire,
            question_text="",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_update_question_text(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Initial question text",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        # Update the question text.
        question.question_text = "Updated question text"
        question.save()
        question.refresh_from_db()
        # __str__ should reflect the updated text (first 30 characters).
        expected_str = f"{self.questionnaire.title} - {'Updated question text'[:30]}"
        self.assertEqual(str(question), expected_str)

    def test_null_category_allowed(self):
        # Category is allowed to be null.
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Question without category",
            question_type="RATING",
            is_required=True,
            category=None,
            sentiment=1
        )
        self.assertIsNone(question.category)

    def test_invalid_sentiment_value(self):
        # Setting a sentiment value not in SENTIMENT_CHOICES should raise a ValidationError.
        question = Question(
            questionnaire=self.questionnaire,
            question_text="Invalid sentiment",
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=0  # Assuming valid sentiments are only 1 and -1.
        )
        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_valid_question_type_agreement(self):
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Do you agree with our terms?",
            question_type="AGREEMENT",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        self.assertEqual(question.question_type, "AGREEMENT")

    def test_is_required_unchanged(self):
        # If is_required is not explicitly set, it should default to True.
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Is this required by default?",
            question_type="RATING",
            category=self.category,
            sentiment=1
        )
        self.assertTrue(question.is_required)

    def test_question_text_preserved(self):
        text = "Exact question text preservation test."
        question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text=text,
            question_type="RATING",
            is_required=True,
            category=self.category,
            sentiment=1
        )
        self.assertEqual(question.question_text, text)
