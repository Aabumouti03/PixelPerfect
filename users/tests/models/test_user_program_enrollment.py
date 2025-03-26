from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserProgramEnrollment
from client.models import Program

User = get_user_model()

class UserProgramEnrollmentTest(TestCase):
    def test_create_enrollment(self):
        user = User.objects.create_user(username='proguser', password='pass')
        end_user = EndUser.objects.create(user=user, age=20)
        program = Program.objects.create(title='Test Program', description='Description')

        enrollment = UserProgramEnrollment.objects.create(user=end_user, program=program)
        self.assertIn(enrollment, program.enrolled_users.all())
        self.assertEqual(str(enrollment), f"{end_user.user.username} enrolled in {program.title}")