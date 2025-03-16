from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question

User = get_user_model()

class DeleteQuestionTest(TestCase):
    def setUp(self):
        """Set up admin and a question."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.questionnaire = Questionnaire.objects.create(title="Survey", description="Contains test questions")
        self.question = Question.objects.create(questionnaire=self.questionnaire, question_text="Sample question?")

        self.client.login(username="admin", password="adminpass")  #Login as admin

    def test_delete_question_successfully(self):
        """Ensure an admin can delete a question from a questionnaire."""
        response = self.client.post(reverse("delete_question", args=[self.question.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())  # Question should be gone
