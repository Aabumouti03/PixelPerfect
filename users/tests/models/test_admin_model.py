from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Admin

User = get_user_model()

class AdminModelTest(TestCase):
    def test_admin_str(self):
        user = User.objects.create_user(
            username='adminUser',
            password='pass',
            first_name='Admin',
            last_name='Test'
        )
        admin_profile = Admin.objects.create(user=user)
        self.assertEqual(str(admin_profile), "Admin: Admin Test")