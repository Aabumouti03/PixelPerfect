from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, Questionnaire_UserResponse
from client.models import Questionnaire

User = get_user_model()

class QuestionnaireUserResponseTest(TestCase):
    def test_questionnaire_user_response(self):
        user = User.objects.create_user(username='questuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        questionnaire = Questionnaire.objects.create(title="Q1", description="...")

        q_user_response = Questionnaire_UserResponse.objects.create(user=end_user, questionnaire=questionnaire)
        self.assertIsNotNone(q_user_response.started_at)
        self.assertIsNone(q_user_response.completed_at)