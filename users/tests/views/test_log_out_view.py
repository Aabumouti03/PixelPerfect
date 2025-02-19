"""Unit Tests of the log out view"""
from django.test import TestCase
from django.urls import reverse
from users.forms import LogInForm
from users.models import User
from users.tests.helpers import LogInTester

class LogOutViewTestCase(TestCase, LogInTester):
    """Unit Tests of the log out view"""

    def setUp(self):
        self.url = reverse('log_out')
        self.user = User.objects.create_user(username='dandoe', first_name="Dan", last_name="Doe", email="dandoe@example.org", password='Testuser123')

    # def test_log_out_url(self):
    #     self.assertEqual(self.url, '/log_out/')
    
    # def test_get_log_out(self):
    #     self.client.login(username='dandoe', password='Testuser123')
    #     self.assertTrue(self._is_logged_in())
    #     response = self.client.get(self.url, follow=True)
    #     response_url = reverse('welcome_page')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'welcome_page.html')
    #     self.assertFalse(self._is_logged_in())