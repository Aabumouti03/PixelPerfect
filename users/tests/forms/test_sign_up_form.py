"""Unit Tests of the sign up form"""
from django import forms
from users.forms import UserSignUpForm, EndUserProfileForm
from django.test import TestCase

class SignUpFormTestCase(TestCase):
    """Unit Tests of the sign up form"""

    def setUp(self):
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


    # Form accepts valid input data for "UserSignUpForm" --> the main fields
    def test_valid_user_sign_up_form(self):
        form = UserSignUpForm(data = self.form_input_for_user)
        self.assertTrue(form.is_valid())
        
    # Form accepts valid input data for "EndUserProfileForm" --> additional profile fields
    def test_valid_end_user_sign_up_form(self):
        form = EndUserProfileForm(data = self.form_input_for_end_user)
        self.assertTrue(form.is_valid())
    
    def test_form_has_necessary_user_fields(self):
        form = UserSignUpForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)

        self.assertIn('email', form.fields)
        email_field = form.fields['email']

        self.assertTrue(isinstance(email_field, forms.EmailField))

        self.assertIn('password1', form.fields)
        password_widget = form.fields['password1'].widget
        self.assertTrue(isinstance(password_widget, forms.PasswordInput))

        self.assertIn('password2', form.fields)
        password_confirmation_widget = form.fields['password2'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))
        

    def test_form_has_necessary_end_user_fields(self):
        form = EndUserProfileForm()

        self.assertIn('age', form.fields)
        self.assertIn('sector', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('ethnicity', form.fields)
        self.assertIn('last_time_to_work', form.fields)
        self.assertIn('phone_number', form.fields)


    # Form validates User model
    def test_form_uses_valid_user_model(self):
        self.form_input_for_user['username'] =  ''
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_form_uses_valid_end_user_model(self):
        self.form_input_for_end_user['age'] =  '0'
        form = UserSignUpForm(data = self.form_input_for_end_user)
        self.assertFalse(form.is_valid())

    # Password has the correct format
    def test_form_password_must_contain_uppercase_letter(self):
        pass
    
    def test_form_password_must_contain_lowercase_letter(self):
        pass
    
    def test_form_password_must_contain_number(self):
        pass
    # Password and Password Confirmation are identical
