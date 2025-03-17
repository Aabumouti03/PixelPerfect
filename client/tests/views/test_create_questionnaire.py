from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question
from users.models import EndUser

User = get_user_model()

class CreateQuestionnaireTest(TestCase):
    def setUp(self):
        """Set up admin and normal user."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="userpass")
        self.end_user = EndUser.objects.create(user=self.normal_user, age=30, gender="female", sector="healthcare")

        self.client.login(username="admin", password="adminpass")  # Login as admin

    def test_create_questionnaire_successfully(self):
        """Ensure an admin can create a questionnaire."""
        response = self.client.post(reverse("create_questionnaire"), {
            "title": "Work Readiness Survey",
            "description": "Assessing readiness to return to work",
        })
        self.assertEqual(response.status_code, 302)  #Redirects after successful creation
        self.assertTrue(Questionnaire.objects.filter(title="Work Readiness Survey").exists())

    def test_non_admin_cannot_create_questionnaire(self):
        """Ensure non-admin users are redirected to login when accessing the create view."""
        self.client.logout()  # Ensure user is logged out

        response = self.client.get(reverse("create_questionnaire"), follow=True)

        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('create_questionnaire')}")
