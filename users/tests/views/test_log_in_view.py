"""Unit Tests of the log in view"""
from django.test import TestCase
from django.urls import reverse
from users.forms import LogInForm
from users.models import User
from users.tests.helpers import LogInTester

class LogInViewTestCase(TestCase, LogInTester):
    """Unit Tests of the log in view"""

    def setUp(self):
        self.url = reverse('log_in')
        self.user = User.objects.create_user(username='dandoe', first_name="Dan", last_name="Doe", email="dandoe@example.org", password='Testuser123')


    def test_log_in_urls(self):
        self.assertEqual(self.url, '/log_in/')
    
    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    # def test_unsuccessful_log_in(self):
    #     form_input = {'username': 'dandoe', 'password': 'Wrong'}
    #     response = self.client.post(self.url, form_input)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'log_in.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, LogInForm))
    #     self.assertFalse(form.is_bound)
    #     self.assertFalse(self._is_logged_in())

    # def test_successful_log_in(self):
    #     form_input = {'username': 'dandoe', 'password': 'Testuser123'}
    #     response = self.client.post(self.url, form_input, follow=True)
    #     self.assertTrue(self._is_logged_in())
    #     response_url = reverse('dashboard')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'dashboard.html')