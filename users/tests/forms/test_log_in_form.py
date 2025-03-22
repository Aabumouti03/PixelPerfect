"""Unit Tests for the LogInForm"""
from django import forms
from django.test import TestCase
from django.contrib.auth import get_user_model, authenticate
from users.forms import LogInForm

User = get_user_model()

class LogInFormTestCase(TestCase):
    """Unit tests for the LogInForm."""

    def setUp(self):
        """Create a test user for authentication."""
        self.test_user = User(username='dandoe', email='dandoe@example.org')
        self.test_user.set_password('Testuser123')  # Properly hashes the password
        self.test_user.save()

        self.valid_form_input = {'username': 'dandoe', 'password': 'Testuser123'}


    def test_form_contains_all_required_fields(self):
        """Ensure the form contains both username and password fields."""
        form = LogInForm()
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
        self.assertTrue(isinstance(form.fields['password'].widget, forms.PasswordInput))

    def test_valid_input_is_accepted(self):
        """Ensure form is valid when correct credentials are provided."""
        form = LogInForm(data=self.valid_form_input)
        self.assertTrue(form.is_valid(), msg=form.errors)

        # Authenticate user
        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user, "Authentication failed with valid credentials.")

    def test_blank_username_is_invalid(self):
        """Ensure the form rejects a blank username."""
        self.valid_form_input['username'] = ''
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_blank_password_is_invalid(self):
        """Ensure the form rejects a blank password."""
        self.valid_form_input['password'] = ''
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_invalid_credentials_fail_authentication(self):
        """Ensure incorrect username/password do not authenticate."""
        form = LogInForm(data={'username': 'invaliduser', 'password': 'WrongPass123'})
        self.assertFalse(form.is_valid())

        # Attempt to authenticate
        user = authenticate(username='invaliduser', password='WrongPass123')
        self.assertIsNone(user, "Authentication should fail for invalid credentials.")

    def test_username_with_spaces_is_invalid(self):
        """Ensure the form rejects usernames with spaces."""
        self.valid_form_input['username'] = 'dan doe'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_username_with_special_characters(self):
        """Ensure the form rejects usernames with special characters."""
        self.valid_form_input['username'] = 'dan@doe!'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_too_short_username_is_invalid(self):
        """Ensure the form rejects usernames that are too short."""
        self.valid_form_input['username'] = 'da'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_too_short_is_invalid(self):
        """Ensure the form rejects a password that is too short."""
        self.valid_form_input['password'] = '123'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_with_spaces_is_invalid(self):
        """Ensure the form rejects passwords containing spaces."""
        self.valid_form_input['password'] = 'Test user123'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_without_uppercase_is_invalid(self):
        """Ensure the form rejects passwords that lack an uppercase letter."""
        self.valid_form_input['password'] = 'testuser123'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_without_lowercase_is_invalid(self):
        """Ensure the form rejects passwords that lack a lowercase letter."""
        self.valid_form_input['password'] = 'TESTUSER123'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_without_number_is_invalid(self):
        """Ensure the form rejects passwords that lack a numeric character."""
        self.valid_form_input['password'] = 'TestUser'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_common_or_weak_is_invalid(self):
        """Ensure the form rejects a weak password like 'password123'."""
        self.valid_form_input['password'] = 'password123'
        form = LogInForm(data=self.valid_form_input)
        self.assertFalse(form.is_valid())

    def test_password_with_special_characters_is_valid(self):
        """Ensure the form accepts passwords containing special characters."""
        self.test_user.set_password('Test@1234')
        self.test_user.save()

        self.valid_form_input['password'] = 'Test@1234'
        form = LogInForm(data=self.valid_form_input)

        self.assertTrue(form.is_valid(), msg=form.errors)

        user = authenticate(username='dandoe', password='Test@1234')
        self.assertIsNotNone(user, "Authentication should succeed for the correct password.")



    def test_valid_username_and_password(self):
        """Ensure a valid username and password combination is accepted."""
        form = LogInForm(data={'username': 'dandoe', 'password': 'Testuser123'})
        self.assertTrue(form.is_valid(), msg=form.errors)

        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user, "Authentication failed for valid credentials.")

    
    def test_username_with_leading_trailing_spaces(self):
        """
        Ensure the form trims whitespace from username before authentication.
        """
        form = LogInForm(data={'username': '  dandoe  ', 
                               'password': 'Testuser123'})
        self.assertTrue(form.is_valid(), msg=form.errors)

        user = authenticate(username='dandoe', 
                            password='Testuser123')
        self.assertIsNotNone(user, "Authentication should succeed even with extra spaces.")
    
    def test_nonexistent_username_fails(self):
        """Ensure authentication fails for a username that does not exist."""
        form = LogInForm(data={'username': 'unknownuser',
                                'password': 'SomePass123'})
        self.assertFalse(form.is_valid())

        user = authenticate(username='unknownuser', 
                            password='SomePass123')
        self.assertIsNone(user, "Authentication should fail for a non-existent user.")

    def test_password_with_special_characters(self):
        """
        Ensure authentication succeeds when using special characters in password.
        """
        self.test_user.set_password('P@$$w0rd!')
        self.test_user.save()

        form = LogInForm(data={'username': 'dandoe', 
                               'password': 'P@$$w0rd!'})
        self.assertTrue(form.is_valid(), msg=form.errors)

        user = authenticate(username='dandoe', password='P@$$w0rd!')
        self.assertIsNotNone(user, "Authentication should succeed with special characters in password.")
    
    def test_incorrect_password_fails(self):
        """Ensure authentication fails when using an incorrect password."""
        form = LogInForm(data={'username': 'dandoe', 
                               'password': 'WrongPassword'})
        self.assertFalse(form.is_valid())

        user = authenticate(username='dandoe', 
                            password='WrongPassword')
        self.assertIsNone(user, "Authentication should fail with an incorrect password.")

    def test_username_case_insensitive_login(self):
        """Ensure authentication works when username is typed in different cases."""
        form = LogInForm(data={'username': 'DANDOE', 
                               'password': 'Testuser123'})
        self.assertTrue(form.is_valid(), msg=form.errors)

        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)
