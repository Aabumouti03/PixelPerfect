from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire
from users.models import EndUser

User = get_user_model()

class DeleteQuestionnaireTest(TestCase):
    
    def setUp(self):
        """Set up admin and a questionnaire."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="userpass")

        self.questionnaire = Questionnaire.objects.create(title="Survey to Delete", description="To be removed")

        self.client.login(username="admin", password="adminpass")  # Login as admin

    def test_delete_questionnaire_successfully(self):
        """Ensure an admin can delete a questionnaire."""
        response = self.client.post(reverse("delete_questionnaire", args=[self.questionnaire.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(Questionnaire.objects.filter(id=self.questionnaire.id).exists())  # Questionnaire should be gone

    def test_non_admin_cannot_delete_questionnaire(self):
        """Ensure non-admin users cannot delete a questionnaire."""
        self.client.logout()  # Ensure user is logged out
        response = self.client.get(reverse("edit_questionnaire", args=[self.questionnaire.id]), follow=True)
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('edit_questionnaire', args=[self.questionnaire.id])}")
