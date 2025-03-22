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

        # Create a questionnaire and categories
        self.questionnaire = Questionnaire.objects.create(title="Test Questionnaire", is_active=True)
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        # Create questions with different sentiments
        self.positive_question = Question.objects.create(
            questionnaire=self.questionnaire, 
            question_text="Positive Question", 
            question_type="RATING", 
            sentiment=1,  # Positive sentiment
            category=self.category1
        )
        self.negative_question = Question.objects.create(
            questionnaire=self.questionnaire, 
            question_text="Negative Question", 
            question_type="RATING", 
            sentiment=-1,  # Negative sentiment
            category=self.category2
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
        QuestionResponse.objects.create(user_response=self.user_response, question=self.positive_question, rating_value=2)  # Max positive score

        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

    def test_negative_category_scores(self):
        """Ensure programs and modules are suggested for categories with negative scores."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=2)  # Strongly agree to negative statement

        program_recommendations = assess_user_responses_programs(self.end_user)
        module_recommendations = assess_user_responses_modules(self.end_user)

        self.assertIn("Category 2", program_recommendations)
        self.assertIn(self.program2, program_recommendations["Category 2"])

        self.assertIn("Category 2", module_recommendations)
        self.assertIn(self.module2, module_recommendations["Category 2"])

    def test_negative_threshold_not_exceeded(self):
        """Ensure that slightly negative scores do not trigger recommendations."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=-1)  # Mildly disagree with negative statement

        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

    def test_question_without_category(self):
        """Ensure function handles questions that lack a category gracefully."""
        question_no_category = Question.objects.create(
            questionnaire=self.questionnaire, 
            question_text="No Category Question", 
            question_type="RATING", 
            sentiment=-1, 
            category=None
        )
        QuestionResponse.objects.create(user_response=self.user_response, question=question_no_category, rating_value=-2)  # Strongly disagree

        self.assertEqual(assess_user_responses_programs(self.end_user), {})
        self.assertEqual(assess_user_responses_modules(self.end_user), {})

    def test_mixed_responses(self):
        """Ensure that a mix of positive and negative responses results in correct recommendations."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.positive_question, rating_value=2)  # Strongly agree (positive)
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=2)  # Strongly agree (negative)

        program_recommendations = assess_user_responses_programs(self.end_user)
        module_recommendations = assess_user_responses_modules(self.end_user)

        # Should only recommend for Category 2 (negative score), not Category 1 (positive score)
        self.assertIn("Category 2", program_recommendations)
        self.assertIn(self.program2, program_recommendations["Category 2"])

        self.assertIn("Category 2", module_recommendations)
        self.assertIn(self.module2, module_recommendations["Category 2"])

    def test_multiple_questions_same_category(self):
        """Ensure that multiple negative questions in the same category correctly impact the score."""
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=2)  # Strongly agree
        QuestionResponse.objects.create(user_response=self.user_response, question=self.negative_question, rating_value=2)  # Another strong agreement

        program_recommendations = assess_user_responses_programs(self.end_user)
        module_recommendations = assess_user_responses_modules(self.end_user)

        self.assertIn("Category 2", program_recommendations)
        self.assertIn(self.program2, program_recommendations["Category 2"])

        self.assertIn("Category 2", module_recommendations)
        self.assertIn(self.module2, module_recommendations["Category 2"])
