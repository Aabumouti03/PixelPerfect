from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserExerciseProgress
from client.models import Exercise

User = get_user_model()

class UserExerciseProgressTest(TestCase):
    def test_exercise_progress(self):
        user = User.objects.create_user(username='exerciseuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        exercise = Exercise.objects.create(title="Test Exercise")

        progress = UserExerciseProgress.objects.create(user=end_user, exercise=exercise, status='completed')
        self.assertEqual(str(progress), "exerciseuser - Test Exercise: completed")