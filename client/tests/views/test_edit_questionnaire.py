from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question
from users.models import EndUser

User = get_user_model()

class EditQuestionnaireTest(TestCase):
    def setUp(self):
        """Set up admin user and a questionnaire."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="userpass")

        self.questionnaire = Questionnaire.objects.create(
            title="Work Readiness Survey",
            description="Assessing readiness to return to work",
            is_active=True
        )

        self.client.login(username="admin", password="adminpass")  # Login as admin

    def test_edit_questionnaire_successfully(self):
        """Ensure an admin can edit a questionnaire."""
        response = self.client.post(reverse("edit_questionnaire", args=[self.questionnaire.id]), {
            "title": "Updated Survey",
            "description": "Updated description",
        })
        self.assertEqual(response.status_code, 302)  # Redirect after edit
        self.questionnaire.refresh_from_db()
        self.assertEqual(self.questionnaire.title, "Updated Survey")  # Check updated title

    def test_non_admin_cannot_edit_questionnaire(self):
        """Ensure non-admin users cannot edit a questionnaire."""
        self.client.logout()  # Ensure user is logged out

        response = self.client.get(reverse("edit_questionnaire", args=[self.questionnaire.id]), follow=True)

        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('edit_questionnaire', args=[self.questionnaire.id])}")
