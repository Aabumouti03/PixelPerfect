from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.full_name(), 'John Doe')

    def test_user_str_method(self):
        user = User.objects.create_user(username='jane', password='pass',
                                        first_name='Jane', last_name='Doe')
        self.assertEqual(str(user), 'jane')