from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import Question, Questionnaire, Category
from users.models import EndUser, QuestionResponse, Questionnaire_UserResponse
from django.contrib.auth import get_user_model

User = get_user_model()

class QuestionResponseModelTest(TestCase):
    """Test suite for the QuestionResponse model."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.end_user = EndUser.objects.create(user=self.user, age=30, gender="male", sector="IT")

        self.category = Category.objects.create(name="Mental Health")

        self.questionnaire = Questionnaire.objects.create(
            title="Sample Questionnaire", 
            description="A sample test questionnaire."
        )
        
        self.user_response = Questionnaire_UserResponse.objects.create(
            user=self.end_user,
            questionnaire=self.questionnaire
        )
        
        self.rating_question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Rate your experience",
            question_type="RATING",
            category=self.category,
            sentiment=1
        )
        
        self.agreement_question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="Do you agree?",
            question_type="AGREEMENT",
            category=self.category,
            sentiment=1
        )
    
    def test_create_valid_rating_question_response(self):
        """Test creating a valid rating question response."""
        response = QuestionResponse.objects.create(
            user_response=self.user_response,
            question=self.rating_question,
            rating_value=1
        )
        
        self.assertEqual(response.user_response, self.user_response)
        self.assertEqual(response.question, self.rating_question)
        self.assertEqual(response.rating_value, 1)

    def test_create_valid_agreement_question_response(self):
        """Test creating a valid agreement question response."""
        response = QuestionResponse.objects.create(
            user_response=self.user_response,
            question=self.agreement_question,
            rating_value=0
        )
        
        self.assertEqual(response.user_response, self.user_response)
        self.assertEqual(response.question, self.agreement_question)
        self.assertEqual(response.rating_value, 0)
        
    def test_invalid_rating_value_below_range(self):
        """Test that an invalid rating value below -2 raises a validation error."""
        response = QuestionResponse(
            user_response=self.user_response,
            question=self.rating_question,
            rating_value=-3 
        )
        
        with self.assertRaises(ValidationError):
            response.full_clean()
            
    def test_invalid_rating_value_above_range(self):
        """Test that an invalid rating value above 2 raises a validation error."""
        response = QuestionResponse(
            user_response=self.user_response,
            question=self.rating_question,
            rating_value=3
        )
        
        with self.assertRaises(ValidationError):
            response.full_clean()
    
    def test_missing_rating_value_for_rating_question(self):
        """Test that a missing rating value for a 'RATING' question raises a validation error."""
        response = QuestionResponse(
            user_response=self.user_response,
            question=self.rating_question,
            rating_value=None
        )
        
        with self.assertRaises(ValidationError) as e:
            response.clean()
        
        self.assertIn('Rating scale questions require a rating value', str(e.exception))

    def test_missing_rating_value_for_agreement_question(self):
        """Test that a missing rating value for an 'AGREEMENT' question raises a validation error."""
        response = QuestionResponse(
            user_response=self.user_response,
            question=self.agreement_question,
            rating_value=None
        )
        
        with self.assertRaises(ValidationError) as e:
            response.clean()
        
        self.assertIn('Agreement scale questions require a selection', str(e.exception))
    
    def test_valid_rating_range(self):
        """Test valid rating values from -2 to 2."""
        for rating in range(-2, 3):  # From -2 to 2 inclusive
            response = QuestionResponse(
                user_response=self.user_response,
                question=self.rating_question,
                rating_value=rating
            )
            try:
                response.full_clean()
            except ValidationError:
                self.fail(f"Valid rating value '{rating}' raised ValidationError unexpectedly.")
