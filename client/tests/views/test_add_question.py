from django.test import TestCase
from django.urls import reverse
from users.models import User
from client.models import Questionnaire, Question

class AddQuestionTest(TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.client.login(username="admin", password="adminpass")

        # Create a sample questionnaire
        self.questionnaire = Questionnaire.objects.create(
            title="Workplace Readiness Survey",
            description="Assessing readiness to return to work"
        )

    def test_add_question_successfully(self):
        """Ensure an admin can add a question to a questionnaire."""
        response = self.client.post(reverse("add_question", args=[self.questionnaire.id]))

        # ✅ Confirm redirect to edit_questionnaire
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("edit_questionnaire", args=[self.questionnaire.id]))

        # ✅ Ensure the question was created with default values
        self.assertTrue(Question.objects.filter(questionnaire=self.questionnaire, question_text="New Question").exists())

    def test_non_admin_cannot_add_question(self):
        """Ensure non-admin users are redirected to login when trying to add a question."""
        self.client.logout()

        # Create a regular user
        self.normal_user = User.objects.create_user(username="user", email="user@example.com", password="userpass")
        self.client.login(username="user", password="userpass")

        response = self.client.post(reverse("add_question", args=[self.questionnaire.id]), follow=True)

        # Ensure the user is redirected to login
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('add_question', args=[self.questionnaire.id])}")

        #Ensure no question is added
        self.assertFalse(Question.objects.filter(questionnaire=self.questionnaire).exists())
