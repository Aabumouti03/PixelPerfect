import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from unittest.mock import patch
from django.http import HttpRequest
from users.models import EndUser, Questionnaire_UserResponse, QuestionResponse, Questionnaire, Question
from users.views import submit_responses

class SubmitResponsesTest(TestCase):
    """Tests for the submit_responses view"""

    def setUp(self):
        """Setup test data for the submit_responses view"""
        self.client = Client(enforce_csrf_checks=False)  # Bypass CSRF for tests

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
        self.client.force_login(self.user)  # Ensure authentication

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [
                {"questionId": self.question1.id, "value": 1},
                {"questionId": self.question2.id, "value": -2},
            ]
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "redirect_url": "/recommended_programs/"})

        # Ensure responses are saved
        self.assertEqual(Questionnaire_UserResponse.objects.count(), 1)
        self.assertEqual(QuestionResponse.objects.count(), 2)

    def test_unauthenticated_user_cannot_submit_responses(self):
        """Ensure unauthenticated users cannot submit responses"""
        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": self.question1.id, "value": 1}]
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(QuestionResponse.objects.count(), 0)  # No responses saved

    def test_missing_questionnaire_id(self):
        """Ensure a request without questionnaire ID fails"""
        self.client.force_login(self.user)

        payload = {"responses": [{"questionId": self.question1.id, "value": 1}]}

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "Questionnaire ID is missing."})

    def test_invalid_questionnaire_id(self):
        """Ensure a request with an invalid questionnaire ID fails"""
        self.client.force_login(self.user)

        payload = {
            "questionnaireId": 999,  # Non-existent ID
            "responses": [{"questionId": self.question1.id, "value": 1}]
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "message": "Questionnaire not found."})

    def test_invalid_question_id(self):
        """Ensure request with an invalid question ID does not break"""
        self.client.force_login(self.user)

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": 999, "value": 1}]  # Invalid question ID
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)

    @patch("users.models.QuestionResponse.full_clean")
    def test_validation_error_handling(self, mock_full_clean):
        """Ensure validation errors are handled"""
        self.client.force_login(self.user)

        mock_full_clean.side_effect = ValidationError("Invalid data")

        payload = {
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": self.question1.id, "value": 1}]
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_manual_call_submit_responses(self):
        """Manually call the view function to confirm execution"""
        request = HttpRequest()
        request.method = "POST"
        request.user = self.user  # Simulate authenticated user
        request._body = json.dumps({
            "questionnaireId": self.questionnaire.id,
            "responses": [{"questionId": self.question1.id, "value": 1}]
        }).encode("utf-8")

        response = submit_responses(request)  # Manually calling the function

        self.assertEqual(response.status_code, 200)
