from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserModuleProgress
from client.models import Module

User = get_user_model()

class UserModuleProgressTest(TestCase):
    def test_module_progress(self):
        user = User.objects.create_user(
            username='progressuser',
            password='pass',
            first_name='Progress',
            last_name='User'
        )
        end_user = EndUser.objects.create(user=user)
        module = Module.objects.create(title="Progress Module", description="Desc")

        progress = UserModuleProgress.objects.create(user=end_user, module=module, completion_percentage=50.0)
        self.assertEqual(progress.status, 'not_started')
        self.assertEqual(str(progress), "Progress User - Progress Module (not_started)")

        with self.assertRaises(Exception):
            UserModuleProgress.objects.create(user=end_user, module=module)