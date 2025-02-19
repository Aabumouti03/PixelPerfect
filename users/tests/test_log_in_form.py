"""Unit Tests of the log in form"""
from django import forms
from django.test import TestCase

class LogInFormTestCase(TestCase):
    """Unit tests of the log in form."""
    def test_form_contains_all_required_fields(self):
        form = LogInForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
        password_field = form.fields['password']
        self.assertTrue(isinstance(password_field.widget,forms.PasswordInput))