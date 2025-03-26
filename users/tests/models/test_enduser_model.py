from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser

User = get_user_model()

class EndUserModelTest(TestCase):
    def test_create_end_user(self):
        user = User.objects.create_user(username='enduser', password='pass',
                                        first_name='End', last_name='User')
        end_user = EndUser.objects.create(
            user=user,
            age=25,
            gender='male',
            last_time_to_work='1_month',
            sector='it',
        )
        self.assertEqual(str(end_user), 'User: End User')
        self.assertEqual(end_user.age, 25)
        self.assertEqual(end_user.gender, 'male')