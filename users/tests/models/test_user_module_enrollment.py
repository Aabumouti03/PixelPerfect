from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserModuleEnrollment
from client.models import Module

User = get_user_model()

class UserModuleEnrollmentTest(TestCase):
    def test_create_module_enrollment(self):
        user = User.objects.create_user(username='moduser', password='pass')
        end_user = EndUser.objects.create(user=user, age=22)
        module = Module.objects.create(title="Test Module", description="Desc")

        enrollment = UserModuleEnrollment.objects.create(user=end_user, module=module)
        self.assertIn(enrollment, module.enrolled_users.all())
        self.assertEqual(str(enrollment), "moduser started Test Module")