from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import EndUser, UserProgramEnrollment
from client.models import Program, Category
from unittest.mock import patch
import json

User = get_user_model()

class RecommendedProgramsViewTest(TestCase):

    def setUp(self):
        """Create a test user, an EndUser profile, and some programs."""
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

        self.category = Category.objects.create(name="Confidence Building")
        
        self.program1 = Program.objects.create(
            title="Rebuilding Confidence for Work",
            description="A guided program to help individuals regain confidence and prepare for work."
        )
        self.program1.categories.add(self.category)  

        self.program2 = Program.objects.create(
            title="Managing Workplace Stress",
            description="Learn how to handle stress and anxiety in a professional environment."
        )
        self.program2.categories.add(self.category)  

        # Enroll user in one program
        self.enrollment = UserProgramEnrollment.objects.create(user=self.end_user, program=self.program1)

        self.client.force_login(self.user)
        self.recommended_programs_url = reverse("recommended_programs")

    @patch("users.views.assess_user_responses_programs")  #  Mock function to return fake recommendations
    def test_authenticated_user_access(self, mock_assess_programs):
        """Ensure authenticated users can access the recommended programs page."""
        # Mock the function to return our test programs
        mock_assess_programs.return_value = {
            "Confidence Building": [self.program1, self.program2]
        }

        response = self.client.get(self.recommended_programs_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rebuilding Confidence for Work") 
        self.assertContains(response, "Managing Workplace Stress") 

    def test_unauthenticated_user_redirect(self):
        """Ensure unauthenticated users are redirected to the login page."""
        self.client.logout()
        response = self.client.get(self.recommended_programs_url)
        self.assertRedirects(response, f"/log_in/?next={self.recommended_programs_url}")

    @patch("users.views.assess_user_responses_programs")
    def test_program_enrollment_via_ajax(self, mock_assess_programs):
        """Test enrolling in a program via AJAX."""
        mock_assess_programs.return_value = {
            "Confidence Building": [self.program1, self.program2]
        }

        data = {"program_id": self.program2.id, "action": "enroll"}
        response = self.client.post(self.recommended_programs_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})

        # Ensure only one program is enrolled (unenrolls others first)
        self.assertTrue(UserProgramEnrollment.objects.filter(user=self.end_user, program=self.program2).exists())
        self.assertFalse(UserProgramEnrollment.objects.filter(user=self.end_user, program=self.program1).exists())

    @patch("users.views.assess_user_responses_programs")
    def test_program_unenrollment_via_ajax(self, mock_assess_programs):
        """Test unenrolling from a program via AJAX."""
        mock_assess_programs.return_value = {
            "Confidence Building": [self.program1, self.program2]
        }

        data = {"program_id": self.program1.id, "action": "unenroll"}
        response = self.client.post(self.recommended_programs_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})

        # Ensure the user is unenrolled from all programs
        self.assertFalse(UserProgramEnrollment.objects.filter(user=self.end_user).exists())

    @patch("users.views.assess_user_responses_programs")
    def test_invalid_program_id_in_ajax_request(self, mock_assess_programs):
        """Test handling of invalid program ID in AJAX request."""
        mock_assess_programs.return_value = {}

        data = {"program_id": 9999, "action": "enroll"}  # Non-existent program ID
        response = self.client.post(self.recommended_programs_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"status": "error", "message": "Program matching query does not exist."})

    def test_enrolling_in_new_program_removes_previous(self):
        """Ensure that enrolling in a new program unenrolls the user from the previous one."""
        new_program = Program.objects.create(title="New Program", description="Another option")
        
        data = {"program_id": new_program.id, "action": "enroll"}
        response = self.client.post(self.recommended_programs_url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "success"})
        
        # Ensure only one program enrollment exists
        self.assertEqual(UserProgramEnrollment.objects.filter(user=self.end_user).count(), 1)

        # Ensure the enrolled program is the new one
        self.assertTrue(UserProgramEnrollment.objects.filter(user=self.end_user, program=new_program).exists())