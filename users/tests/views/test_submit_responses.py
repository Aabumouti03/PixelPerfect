import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, Questionnaire_UserResponse, QuestionResponse, Questionnaire, Question
from django.utils import timezone

class SubmitResponsesTest(TestCase):
    """Tests for the submit_responses view"""

    def setUp(self):
        """Setup test data for the submit_responses view"""
        self.client = Client()

        # Create a test user
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )
        self.end_user = EndUser.objects.create(user=self.user)

        # Create a questionnaire
        self.questionnaire = Questionnaire.objects.create(
            title="Workplace Readiness Survey",
            description="Survey to assess readiness to return to work",
            is_active=True
        )

        # Create questions
        self.question1 = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="How confident are you in your ability to return to work?",
            question_type="AGREEMENT",
            sentiment=1
        )

        self.question2 = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="How would you rate your current mental well-being?",
            question_type="RATING",
            sentiment=-1
        )

        # Set up the URL for the submit_responses view
        self.url = reverse("submit_responses")

    def test_authenticated_user_can_submit_responses(self):
        """Ensure an authenticated user can submit responses successfully"""
        self.client.login(username="testuser", password="testpass")

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [
                {"questionId": self.question1.id, "value": 4},
                {"questionId": self.question2.id, "value": 3},
            ]
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "redirect_url": "/recommended_programs/"})

        # Ensure responses are saved
        self.assertEqual(Questionnaire_UserResponse.objects.count(), 1)
        self.assertEqual(QuestionResponse.objects.count(), 2)

    def test_unauthenticated_user_cannot_submit_responses(self):
        """Ensure unauthenticated users cannot submit responses"""
        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": self.question1.id, "value": 4}]
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(QuestionResponse.objects.count(), 0)  # No responses saved

    def test_missing_questionnaire_id(self):
        """Ensure a request without questionnaire ID fails"""
        self.client.login(username="testuser", password="testpass")

        payload = {
            "responses": [{"questionId": self.question1.id, "value": 4}]
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "Questionnaire ID is missing."})

    def test_invalid_questionnaire_id(self):
        """Ensure a request with an invalid questionnaire ID fails"""
        self.client.login(username="testuser", password="testpass")

        payload = {
            "questionnaireId": 999,  # Non-existent ID
            "responses": [{"questionId": self.question1.id, "value": 4}]
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "Questionnaire not found."})

    def test_missing_responses(self):
        """Ensure a request without responses fails"""
        self.client.login(username="testuser", password="testpass")

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": []
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "No responses provided."})

    def test_invalid_question_id(self):
        """Ensure a request with an invalid question ID fails"""
        self.client.login(username="testuser", password="testpass")

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": 999, "value": 4}]  # Non-existent question ID
        }

        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "redirect_url": "/recommended_programs/"})

        # Ensure no invalid responses are saved
        self.assertEqual(QuestionResponse.objects.count(), 0)

    def test_invalid_request_method(self):
        """Ensure a GET request is not allowed"""
        self.client.login(username="testuser", password="testpass")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "Invalid request method"})
