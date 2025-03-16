from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, Questionnaire_UserResponse, QuestionResponse
from client.models import Program, Module, Category, Question, Questionnaire
from users.helpers_questionnaire import assess_user_responses_programs, assess_user_responses_modules

class AssessUserResponsesTest(TestCase):
    def setUp(self):
        """Set up test data for all test cases."""
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.end_user = EndUser.objects.create(user=self.user, age=25, gender="male", last_time_to_work="1_year", sector="it")

        # Create a questionnaire and category
        self.questionnaire = Questionnaire.objects.create(title="Test Questionnaire", is_active=True)
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        # Create questions with different sentiments
        self.positive_question = Question.objects.create(
            questionnaire=self.questionnaire, question_text="Positive Question", question_type="RATING", sentiment=1, category=self.category1
        )
        self.negative_question = Question.objects.create(
            questionnaire=self.questionnaire, question_text="Negative Question", question_type="RATING", sentiment=-1, category=self.category2
        )

        # Create a response session for the user
        self.user_response = Questionnaire_UserResponse.objects.create(user=self.end_user, questionnaire=self.questionnaire)

        # Create programs and modules linked to categories
        self.program1 = Program.objects.create(title="Program 1")
        self.program1.categories.add(self.category1)

        self.program2 = Program.objects.create(title="Program 2")
        self.program2.categories.add(self.category2)

        self.module1 = Module.objects.create(title="Module 1")
        self.module1.categories.add(self.category1)

        self.module2 = Module.objects.create(title="Module 2")
        self.module2.categories.add(self.category2)

    def test_no_questionnaire_responses(self):
        """Ensure function returns an empty dictionary when there are no responses."""
        self.user_response.delete()  # Remove existing responses
        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

    def test_all_positive_scores(self):
        """Ensure no programs or modules are recommended when all scores are positive."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.positive_question, rating_value=5)
        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

    def test_negative_category_scores(self):
        """Ensure programs and modules are suggested for categories with negative scores."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=5)

        program_recommendations = assess_user_responses_programs(self.end_user)
        module_recommendations = assess_user_responses_modules(self.end_user)

        self.assertIn("Category 2", program_recommendations)
        self.assertIn(self.program2, program_recommendations["Category 2"])

        self.assertIn("Category 2", module_recommendations)
        self.assertIn(self.module2, module_recommendations["Category 2"])

    def test_question_without_category(self):
        """Ensure function handles questions that lack a category."""
        question_no_category = Question.objects.create(
            questionnaire=self.questionnaire, question_text="No Category Question", question_type="RATING", sentiment=-1, category=None
        )
        QuestionResponse.objects.create(user_response=self.user_response, question=question_no_category, rating_value=3)

        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

