from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import Questionnaire, Question

try:
    from client.models import Category
except ImportError:
    from django.db import models
    class Category(models.Model):
        name = models.CharField(max_length=100)
        def __str__(self):
            return self.name

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
        self.assertIn(question, self.questionnaire.questions.all())
