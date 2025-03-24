from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, Program, Module, Questionnaire, Questionnaire_UserResponse

User = get_user_model()  # ✅ Use the correct user model

class UserDetailViewTest(TestCase):
    
    def setUp(self):
        """Set up test data before running each test."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.end_user = EndUser.objects.create(user=self.user)

        # ✅ Create a Questionnaire first
        self.questionnaire = Questionnaire.objects.create(title="Test Questionnaire")

        # ✅ Create a Questionnaire_UserResponse and link it to the questionnaire
        self.questionnaire_response = Questionnaire_UserResponse.objects.create(
            user=self.end_user,
            questionnaire=self.questionnaire  # ✅ Fix: Assign a valid questionnaire
        )

        # ✅ Create a test program and module
        self.program = Program.objects.create(title="Test Program", description="A test program.")
        self.module = Module.objects.create(title="Test Module", description="A test module.")

        # ✅ Enroll user in the program and module
        UserProgramEnrollment.objects.create(user=self.end_user, program=self.program)
        UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)

        # ✅ URL for the user detail view
        self.user_detail_url = reverse('user_detail_view', args=[self.user.id])

    def test_authenticated_user_can_access(self):
        """Test that a logged-in user can access their detail page."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/user_detail.html")
        self.assertEqual(response.context["user"], self.end_user)
        enrolled_programs = [enrollment.program for enrollment in response.context["enrolled_programs"]]
        self.assertIn(self.program, enrolled_programs)

        # ✅ Extract `module` from `UserModuleEnrollment`
        enrolled_modules = [enrollment.module for enrollment in response.context["enrolled_modules"]]
        self.assertIn(self.module, enrolled_modules)

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, 302)  # 302 Redirect
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_nonexistent_user_returns_404(self):
        """Test that accessing a non-existing user profile returns a 404 error."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('user_detail_view', args=[9999]))  # Nonexistent user ID
        self.assertEqual(response.status_code, 404)
