from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, Program, Module, Questionnaire, Questionnaire_UserResponse
from client.views import admin_check

User = get_user_model()

class UserDetailViewTest(TestCase):
    
    def setUp(self):
        """Set up test data before running each test."""
        self.user = User.objects.create_user(username="testuser", password="testpass", email="user@example.com")
        self.end_user = EndUser.objects.create(user=self.user)

        self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpass", email="admin@example.com")
        self.admin_end_user = EndUser.objects.create(user=self.admin_user)

        self.questionnaire = Questionnaire.objects.create(title="Test Questionnaire")
        self.questionnaire_response = Questionnaire_UserResponse.objects.create(
            user=self.end_user,
            questionnaire=self.questionnaire
        )

        self.program = Program.objects.create(title="Test Program", description="A test program.")
        self.module = Module.objects.create(title="Test Module", description="A test module.")

        UserProgramEnrollment.objects.create(user=self.end_user, program=self.program)
        UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)

        self.user_detail_url = reverse('user_detail_view', args=[self.user.id])

    def test_admin_can_access_user_detail(self):
        """Test that an admin user can access the user detail page."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/user_detail.html")
        self.assertEqual(response.context["user"], self.end_user)

        enrolled_programs = [enrollment.program for enrollment in response.context["enrolled_programs"]]
        self.assertIn(self.program, enrolled_programs)

        enrolled_modules = [enrollment.module for enrollment in response.context["enrolled_modules"]]
        self.assertIn(self.module, enrolled_modules)

    def test_non_admin_user_is_redirected(self):
        """Test that a non-admin user is denied access."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.user_detail_url)

        self.assertEqual(response.status_code, 302)
        expected_url = settings.LOGIN_URL + f"?next={self.user_detail_url}"
        self.assertEqual(response.url, expected_url)

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_nonexistent_user_returns_404(self):
        """Test that accessing a non-existing user profile returns a 404 error."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.get(reverse('user_detail_view', args=[9999]))
        self.assertEqual(response.status_code, 404)
