from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire
from users.models import EndUser

User = get_user_model()


class ActivateQuestionnaireTest(TestCase):
    """Test suite for activate_questionnaire view"""

    def setUp(self):
        """Create test users and sample questionnaires"""
        self.client = Client()

        # Create an admin user and EndUser profile
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.admin_profile = EndUser.objects.create(user=self.admin_user, age=35, gender="male", sector="it")

        # Create a normal user and EndUser profile
        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )
        self.end_user = EndUser.objects.create(user=self.normal_user, age=30, gender="female", sector="healthcare")

        # Create sample questionnaires
        self.q1 = Questionnaire.objects.create(title="Workplace Readiness Survey", is_active=True)
        self.q2 = Questionnaire.objects.create(title="Mental Health at Work Survey", is_active=False)

    def test_redirect_if_not_logged_in(self):
        """Test that non-authenticated users are redirected"""
        response = self.client.post(reverse("activate_questionnaire", args=[self.q2.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("activate_questionnaire", args=[self.q2.id])
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a normal user is redirected and cannot activate a questionnaire"""
        self.client.login(username="user", password="userpass")
        response = self.client.post(reverse("activate_questionnaire", args=[self.q2.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("activate_questionnaire", args=[self.q2.id])
        self.assertRedirects(response, expected_url)

    def test_admin_can_activate_questionnaire(self):
        """Test that an admin can activate a questionnaire"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.post(reverse("activate_questionnaire", args=[self.q2.id]))

        # Refresh from DB to get the latest values
        self.q1.refresh_from_db()
        self.q2.refresh_from_db()

        # Ensure only q2 is active, and q1 is deactivated
        self.assertFalse(self.q1.is_active)
        self.assertTrue(self.q2.is_active)

        # Ensure redirection to manage questionnaires page
        self.assertRedirects(response, reverse("manage_questionnaires"))
