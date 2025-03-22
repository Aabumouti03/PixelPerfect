from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from users.forms import UserSignUpForm, EndUserProfileForm
from users.models import User
from django.test import TestCase

class SignUpFormTestCase(TestCase):
    """Unit Tests for the sign-up forms."""

    def setUp(self):
        self.form_input_for_user = {
            'username': 'dandoe',
            'first_name': 'Dan',
            'last_name': 'Doe',
            'email': 'dandoe@example.org',
            'password1': 'Testuser123',
            'password2': 'Testuser123'
        }
        self.form_input_for_end_user = {
            'age': '20',
            'gender': 'male',  # Now required, must be valid
            'sector': 'healthcare',  # Now required, must be valid
            'ethnicity': 'asian',  # Now required, must be valid
            'last_time_to_work': '1_month',  # Now required, must be valid
            'phone_number': '1234567890'
        }

    def test_valid_user_sign_up_form(self):
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertTrue(form.is_valid())
    
    def test_valid_end_user_sign_up_form(self):
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertTrue(form.is_valid())
    
    def test_gender_cannot_be_empty(self):
        """Ensure form is invalid if 'gender' is left unselected."""
        self.form_input_for_end_user['gender'] = ''
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())
        self.assertIn('gender', form.errors)

    def test_sector_cannot_be_empty(self):
        """Ensure form is invalid if 'sector' is left unselected."""
        self.form_input_for_end_user['sector'] = ''
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())
        self.assertIn('sector', form.errors)

    def test_last_time_to_work_cannot_be_empty(self):
        """Ensure form is invalid if 'last_time_to_work' is left unselected."""
        self.form_input_for_end_user['last_time_to_work'] = ''
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_time_to_work', form.errors)

    def test_form_invalid_with_empty_username(self):
        self.form_input_for_user['username'] = ''
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
    
    def test_form_invalid_with_invalid_email(self):
        self.form_input_for_user['email'] = 'invalid-email'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
    
    def test_password_must_contain_uppercase_letter(self):
        self.form_input_for_user['password1'] = 'testuser123'
        self.form_input_for_user['password2'] = 'testuser123'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
    
    def test_password_must_contain_lowercase_letter(self):
        self.form_input_for_user['password1'] = 'TESTUSER123'
        self.form_input_for_user['password2'] = 'TESTUSER123'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
    
    def test_password_must_contain_number(self):
        self.form_input_for_user['password1'] = 'TestUser'
        self.form_input_for_user['password2'] = 'TestUser'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
    
    def test_password_and_confirmation_must_match(self):
        self.form_input_for_user['password2'] = 'DifferentPass123'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_invalid_phone_number(self):
        self.form_input_for_end_user['phone_number'] = 'abcdefg'
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())

    def test_invalid_age(self):
        self.form_input_for_end_user['age'] = '-5'
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())

    def test_username_with_whitespace(self):
        self.form_input_for_user['username'] = ' user name '
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_duplicate_username(self):
        User.objects.create(username='dandoe', email='dandoe@example.org', password='Testuser123')
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_first_name_cannot_contain_numbers_or_special_chars(self):
        self.form_input_for_user["first_name"] = "John123!"
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_last_name_cannot_contain_numbers_or_special_chars(self):
        self.form_input_for_user["last_name"] = "Doe@#$"
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_password_should_not_be_common(self):
        self.form_input_for_user["password1"] = "password123"
        self.form_input_for_user["password2"] = "password123"
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_phone_number_too_short(self):
        self.form_input_for_end_user["phone_number"] = "12345"
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())

    def test_password_cannot_contain_spaces(self):
        self.form_input_for_user["password1"] = "Test user123"
        self.form_input_for_user["password2"] = "Test user123"
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_username_too_short(self):
        self.form_input_for_user['username'] = 'ab'
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_age_too_high(self):
        self.form_input_for_end_user['age'] = '150'
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())

    def test_password_too_short(self):
        self.form_input_for_user["password1"] = "Aa1"
        self.form_input_for_user["password2"] = "Aa1"
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())

    def test_phone_number_too_long(self):
        self.form_input_for_end_user["phone_number"] = "1234567890123456789"
        form = EndUserProfileForm(data=self.form_input_for_end_user)
        self.assertFalse(form.is_valid())
        
    def test_username_duplicate_case_insensitive(self):
        """Ensure duplicate usernames are rejected even if they differ in casing."""
        User.objects.create(username='Dandoe', email='another@example.org')
        form = UserSignUpForm(data=self.form_input_for_user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
