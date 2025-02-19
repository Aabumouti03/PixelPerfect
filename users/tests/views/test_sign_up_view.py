"""Unit Tests of the sign up view"""
from django.test import TestCase
from users.forms import UserSignUpForm
from users.models import User
from django.urls import reverse
from users.tests.helpers import LogInTester
from django.contrib.auth.hashers import check_password

class SignUpViewTestCase(TestCase, LogInTester):
    """Unit Tests of the sign up view"""

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input_for_user = {
            'username': 'dandoe',
            'first_name':'Dan',
            'last_name':'Doe',
            'email':'dandoe@example.org',
            'password1':'Testuser123',
            'password2':'Testuser123'
        }

        self.form_input_for_end_user = {
            'age': '20',
            'gender':'male',
            'sector':'healthcare',
            'ethnicity':'asian',
            'last_time_to_work':'1_month',
            'phone_number':'11111111'
        }
    
    def test_sign_up_url(self):
        self.assertTrue(self.url, '/sign_up/')
    
    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, UserSignUpForm))
        self.assertFalse(form.is_bound)


    # def test_unsuccessful_sign_up(self):
    #     before_count = User.objects.count()
    #     form_input = {**self.form_input_for_user, **self.form_input_for_end_user}  

    #     form_input['username'] = 'WRONG_USERNAME'

    #     response = self.client.post(self.url, form_input)

    #     after_count = User.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'sign_up.html')
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, UserSignUpForm))
    #     self.assertTrue(form.is_bound)
    #     self.assertFalse(self._is_logged_in())

    
    # def test_successful_sign_up(self):
    #     before_count = User.objects.count()
    #     form_input = {**self.form_input_for_user, **self.form_input_for_end_user}  
    #     response = self.client.post(self.url, form_input, follow=True)

    #     after_count = User.objects.count()
    #     self.assertEqual(after_count, before_count + 1)

    #     response_url = reverse('log_in')
    #     self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'log_in.html')
    #     user = User.objects.get(username='dandoe')
    #     self.assertEqual(user.first_name, 'Dan')
    #     self.assertEqual(user.last_name, 'Doe')
    #     self.assertEqual(user.email, 'dandoe@example.org')

    #     self.assertTrue(check_password('Testuser123', user.password))
    #     self.assertTrue(self._is_logged_in())

        
