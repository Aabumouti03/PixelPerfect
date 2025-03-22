from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import EndUser, UserModuleEnrollment, Module
from unittest.mock import patch  #  Mocking the function
import json

User = get_user_model()

class RecommendedModulesViewTest(TestCase):

    def setUp(self):
        """Create a test user, an EndUser profile, and some modules."""
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Test@1234"
        )
        self.end_user = EndUser.objects.create(
            user=self.user,
            phone_number="+123456789",
            age=25,
            gender="male",
            ethnicity="asian",
            last_time_to_work="1_month",
            sector="IT"
        )

        # 📌 Create some modules
        self.module1 = Module.objects.create(
            title="Rebuilding Confidence for Work",
            description="A guided program to help individuals regain self-confidence."
        )
        self.module2 = Module.objects.create(
            title="Managing Workplace Anxiety",
            description="Learn techniques to handle stress, anxiety, and pressure."
        )

        # 📌 Enroll the user in one module
        self.enrollment = UserModuleEnrollment.objects.create(user=self.end_user, module=self.module1)

        self.client.force_login(self.user)
        self.recommended_modules_url = reverse("recommended_modules")

    @patch("users.views.assess_user_responses_modules")  #  Mock the function
    def test_authenticated_user_access(self, mock_assess_function):
        """Ensure authenticated users can access the recommended modules page with mocked recommendations."""

        mock_assess_function.return_value = {
            "Confidence": [self.module1],
            "Anxiety": [self.module2]
        }

        response = self.client.get(self.recommended_modules_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rebuilding Confidence for Work")  
        self.assertContains(response, "Managing Workplace Anxiety")  

    def test_unauthenticated_user_redirect(self):
        """Ensure unauthenticated users are redirected to the login page."""
        self.client.logout()
        response = self.client.get(self.recommended_modules_url)
        self.assertRedirects(response, f"/log_in/?next={self.recommended_modules_url}")

    def test_module_enrollment_via_ajax(self):
        """Test enrolling in a module via AJAX."""
        data = {"module_id": self.module2.id, "action": "enroll"}
        response = self.client.post(self.recommended_modules_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertTrue(UserModuleEnrollment.objects.filter(user=self.end_user, module=self.module2).exists())

    def test_module_unenrollment_via_ajax(self):
        """Test unenrolling from a module via AJAX."""
        data = {"module_id": self.module1.id, "action": "unenroll"}
        response = self.client.post(self.recommended_modules_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        self.assertFalse(UserModuleEnrollment.objects.filter(user=self.end_user, module=self.module1).exists())

    def test_invalid_module_id_in_ajax_request(self):
        """Test handling of invalid module ID in AJAX request."""
        data = {"module_id": 9999, "action": "enroll"}  # Non-existent module ID
        response = self.client.post(self.recommended_modules_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "error", "message": "Module matching query does not exist."})


