from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question

User = get_user_model()

class QuestionnaireViewTest(TestCase):
    def setUp(self):
        """Set up test data."""
        # Create a user and log in
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")  # ✅ LOG IN

        # Create an active questionnaire
        self.questionnaire = Questionnaire.objects.create(title="Workplace Readiness Survey", is_active=True)

        # Create questions
        self.question1 = Question.objects.create(
            questionnaire=self.questionnaire, question_text="How ready are you?", question_type="AGREEMENT"
        )

    def test_questionnaire_view_with_active_questionnaire(self):
        """Ensure the questionnaire page loads with active questions."""
        response = self.client.get(reverse("questionnaire"))

        # Check response status (should be 200)
        self.assertEqual(response.status_code, 200)

        # Ensure question is present
        self.assertContains(response, "How ready are you?")

    def test_questionnaire_view_without_active_questionnaire(self):
        """Ensure the questionnaire page loads without questions if no active questionnaire."""
        self.questionnaire.is_active = False
        self.questionnaire.save()

        response = self.client.get(reverse("questionnaire"))

        # ✅ Check response status (should be 200)
        self.assertEqual(response.status_code, 200)

        # ✅ Ensure no questions are shown
        self.assertNotContains(response, "How ready are you?")
