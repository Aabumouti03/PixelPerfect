from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserProgramProgress
from client.models import Program

User = get_user_model()

class UserProgramProgressTest(TestCase):
    def test_user_program_progress_str(self):
        user = User.objects.create_user(username='testprog', password='pass',
                                        first_name='Prog', last_name='User')
        end_user = EndUser.objects.create(user=user)
        program = Program.objects.create(title='My Program')
        progress = UserProgramProgress.objects.create(user=end_user, program=program, status='in_progress')
        
        self.assertEqual(str(progress), "Prog User - My Program (in_progress)")