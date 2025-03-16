from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question
from users.models import EndUser

User = get_user_model()


class ViewQuestionnaireTest(TestCase):
    """Test suite for view_questionnaire view"""

    def setUp(self):
        """Create test users and sample questionnaire"""
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

        # Create a questionnaire
        self.questionnaire = Questionnaire.objects.create(title="Workplace Readiness Survey", is_active=True)

        # Add sample questions
        self.question1 = Question.objects.create(
            questionnaire=self.questionnaire, question_text="Do you feel confident returning to work?", question_type="AGREEMENT"
        )
        self.question2 = Question.objects.create(
            questionnaire=self.questionnaire, question_text="What challenges do you expect when returning?", question_type="RATING"
        )

    def test_redirect_if_not_logged_in(self):
        """Test that non-authenticated users are redirected"""
        response = self.client.get(reverse("view_questionnaire", args=[self.questionnaire.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("view_questionnaire", args=[self.questionnaire.id])
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a normal user is redirected and cannot view the questionnaire"""
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("view_questionnaire", args=[self.questionnaire.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("view_questionnaire", args=[self.questionnaire.id])
        self.assertRedirects(response, expected_url)

    def test_admin_can_view_questionnaire(self):
        """Test that an admin can view the questionnaire"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("view_questionnaire", args=[self.questionnaire.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/view_questionnaire.html")
        self.assertContains(response, "Workplace Readiness Survey")
        self.assertContains(response, "Do you feel confident returning to work?")
        self.assertContains(response, "What challenges do you expect when returning?")
