from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question

import json

User = get_user_model()

class QuestionnaireViewTest(TestCase):
    def setUp(self):
        """Set up user and data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.url = reverse("questionnaire")

    def test_questionnaire_view_with_active_questionnaire(self):
        """Ensure the questionnaire view works when an active questionnaire exists."""
        # Create active questionnaire with one question
        questionnaire = Questionnaire.objects.create(title="Workplace Readiness Survey", is_active=True)
        Question.objects.create(
            questionnaire=questionnaire,
            question_text="How ready are you?",
            question_type="AGREEMENT"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")
        self.assertContains(response, "How ready are you?")
        self.assertIn("questions_json", response.context)

        questions_json = json.loads(response.context["questions_json"])
        self.assertEqual(len(questions_json), 1)
        self.assertEqual(questions_json[0]["question_text"], "How ready are you?")
        self.assertEqual(questions_json[0]["question_type"], "AGREEMENT")

    def test_questionnaire_view_without_active_questionnaire(self):
        """Ensure view renders even when no questionnaire is active."""
        Questionnaire.objects.create(title="Old Survey", is_active=False)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")

        self.assertIn("questions_json", response.context)
        questions_data = json.loads(response.context["questions_json"])
        self.assertEqual(questions_data, [])

        # No questions shown
        self.assertNotContains(response, "How ready are you?")

    def test_questionnaire_view_with_no_questionnaire_at_all(self):
        """Ensure view doesn't break if no questionnaires exist at all."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")

        self.assertIn("questions_json", response.context)
        self.assertEqual(json.loads(response.context["questions_json"]), [])
        self.assertIsNone(response.context["active_questionnaire"])
