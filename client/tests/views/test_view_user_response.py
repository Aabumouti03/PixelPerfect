from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from users.models import EndUser, Questionnaire_UserResponse, QuestionResponse
from client.models import Questionnaire, Question

User = get_user_model()

class ViewUserResponseTest(TestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass",
            first_name="Admin", last_name="User"
        )

        # Create a normal user (respondent)
        self.normal_user = User.objects.create_user(
            username="user1", email="user1@example.com", password="userpass",
            first_name="John", last_name="Doe"
        )
        self.end_user = EndUser.objects.create(user=self.normal_user, age=30, gender="female", sector="healthcare")

        # Create a questionnaire
        self.questionnaire = Questionnaire.objects.create(
            title="Workplace Readiness Survey",
            description="Assessing readiness to return to work",
            is_active=True
        )

        # Create a question
        self.question = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="How confident are you in your ability to return to work?",
            question_type="AGREEMENT"
        )

        # Create a user response
        self.user_response = Questionnaire_UserResponse.objects.create(
            questionnaire=self.questionnaire, user=self.end_user
        )

        # Create an answer for the question
        self.question_response = QuestionResponse.objects.create(
            user_response=self.user_response,
            question=self.question,
            rating_value=4  # Agreement scale response (1-5)
        )

    def test_admin_can_view_user_response(self):
        """Test that an admin can view a user's questionnaire response."""
        self.client.login(username="admin", password="adminpass")

        response = self.client.get(reverse("view_user_response", args=[self.user_response.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.questionnaire.title)  # Check for questionnaire title
        self.assertContains(response, self.question.question_text)  #Ensure question is displayed
        self.assertContains(response, "Agree")  # Check for converted text label instead of "4"


    def test_non_admin_cannot_view_user_response(self):
        """Test that a non-admin user CANNOT view another user's response."""
        self.client.login(username="user1", password="userpass")

        response = self.client.get(reverse("view_user_response", args=[self.user_response.id]), follow=True)

        self.assertRedirects(response, "/log_in/?next=/user_response/1/")  # Expect redirect to login page
