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

    def test_questionnaire_view_with_multiple_questions(self):
        """Ensure the view returns all questions from an active questionnaire."""
        questionnaire = Questionnaire.objects.create(title="Multiple Qs", is_active=True)
        Question.objects.create(questionnaire=questionnaire, question_text="Q1", question_type="TEXT")
        Question.objects.create(questionnaire=questionnaire, question_text="Q2", question_type="CHOICE")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")

        questions = json.loads(response.context["questions_json"])
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["question_text"], "Q1")
        self.assertEqual(questions[1]["question_type"], "CHOICE")

    def test_questionnaire_view_returns_questions_in_order(self):
        """Ensure questions are returned in the order they were created."""
        questionnaire = Questionnaire.objects.create(title="Ordered Survey", is_active=True)
        q1 = Question.objects.create(questionnaire=questionnaire, question_text="First?", question_type="TEXT")
        q2 = Question.objects.create(questionnaire=questionnaire, question_text="Second?", question_type="TEXT")
        q3 = Question.objects.create(questionnaire=questionnaire, question_text="Third?", question_type="TEXT")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        questions = json.loads(response.context["questions_json"])
        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0]["id"], q1.id)
        self.assertEqual(questions[1]["id"], q2.id)
        self.assertEqual(questions[2]["id"], q3.id)


    def test_questionnaire_view_without_active_questionnaire(self):
        """Ensure view renders even when no questionnaire is active."""
        Questionnaire.objects.create(title="Old Survey", is_active=False)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")

        self.assertIn("questions_json", response.context)
        questions_data = json.loads(response.context["questions_json"])
        self.assertEqual(questions_data, [])

        self.assertNotContains(response, "How ready are you?")

    def test_questionnaire_view_with_no_questionnaire_at_all(self):
        """Ensure view doesn't break if no questionnaires exist at all."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/questionnaire.html")

        self.assertIn("questions_json", response.context)
        self.assertEqual(json.loads(response.context["questions_json"]), [])
        self.assertIsNone(response.context["active_questionnaire"])

    def test_questionnaire_view_requires_login(self):
        """Ensure anonymous users are redirected if login is required."""
        self.client.logout()
        response = self.client.get(self.url)

        # Adjust this if the view is public!
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in", response.url)
