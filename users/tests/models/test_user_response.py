from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserResponse
from client.models import ExerciseQuestion

User = get_user_model()

class UserResponseTest(TestCase):
    def test_create_user_response(self):
        user = User.objects.create_user(username='resuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        exercise_question = ExerciseQuestion.objects.create(question_text="Sample Q")

        user_response = UserResponse.objects.create(
            user=end_user,
            question=exercise_question,
            response_text="User's answer"
        )
        self.assertEqual(str(user_response), f"Response by resuser for {exercise_question}")