from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserGravatarTest(TestCase):
    def test_gravatar(self):
        user = User.objects.create_user(username='gravuser', password='pass', email='test@example.com')
        url = user.gravatar(size=200)
        self.assertIn('size=200', url)
        self.assertIn('www.gravatar.com', url)

    def test_mini_gravatar(self):
        user = User.objects.create_user(username='minigrav', password='pass', email='mini@example.com')
        url = user.mini_gravatar()
        self.assertIn('size=60', url)
        self.assertIn('www.gravatar.com', url)