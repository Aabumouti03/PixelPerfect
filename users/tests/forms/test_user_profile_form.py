from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from users.models import EndUser  
from users.forms import UserProfileForm

User = get_user_model()


class UserProfileFormTest(TestCase):

    def setUp(self):
        """Create a user for testing unique constraints."""
        self.user = User.objects.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password="Test@1234"
        )

        self.end_user = EndUser.objects.create(
            user=self.user,
            phone_number="+123456789",
            age=25,
            gender="male",
            ethnicity="asian",
            last_time_to_work="1_month",
            sector="it"
        )

        # Explicitly set a unique `new_email` for this test
        self.user.email = "unique_test@example.com"
        self.user.save()

    def test_valid_form(self):
        """Test a valid form submission."""

        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": self.user.email,  # Use the existing email
            "new_email": "unique_johndoe_new@example.com",  # Ensure uniqueness
            "new_password": "StrongPass123!",
            "confirm_password": "StrongPass123!",
            "phone_number": "+987654321",
            "age": 30,
            "gender": "female",
            "ethnicity": "hispanic",
            "last_time_to_work": "1_month",
            "sector": "finance",
        }
        form = UserProfileForm(data=form_data, instance=self.end_user, user=self.user)
             
        self.assertTrue(form.is_valid())

            # Simulate the email verification step
        self.user.new_email = form.cleaned_data.get("new_email")
        self.user.save()

            # Ensure new_email is stored but email is unchanged
        self.assertEqual(self.user.new_email, "unique_johndoe_new@example.com")
        self.assertNotEqual(self.user.email, self.user.new_email)

        # Now simulate email verification
        self.user.email = self.user.new_email
        self.user.new_email = None
        self.user.email_verified = True
        self.user.save()

        # Ensure email is now updated
        self.assertEqual(self.user.email, "unique_johndoe_new@example.com")
        self.assertIsNone(self.user.new_email)

    def test_missing_required_fields(self):
        """Test form validation when required fields are missing."""
        form_data = {}  # Empty form
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)
        self.assertIn("username", form.errors)
        self.assertIn("age", form.errors)

    def test_invalid_first_name(self):
        """Test first name with invalid characters and blank/overlong cases."""
        invalid_first_names = ["John123", "Doe!", "", "A" * 51]  # Includes blank & max_length violation
        for first_name in invalid_first_names:
            form_data = {"first_name": first_name}
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("first_name", form.errors)

    def test_invalid_last_name(self):
        """Test last name with invalid characters and blank/overlong cases."""
        invalid_last_names = ["Doe123", "Smith!", "", "B" * 51]  # Includes blank & max_length violation
        for last_name in invalid_last_names:
            form_data = {"last_name": last_name}
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("last_name", form.errors)

    def test_invalid_username(self):
        """Test username validation rules, including blank & max_length cases."""
        invalid_usernames = ["a", "test user", "user@123", "", "C" * 31]  # Includes blank & max_length violation
        for username in invalid_usernames:
            form_data = {"username": username}
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("username", form.errors)

    def test_duplicate_username(self):
        """Test username uniqueness validation."""
        form_data = {"username": "testuser"}  # Already exists in setUp
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_invalid_phone_number(self):
        """Test invalid phone numbers."""
        invalid_phone_numbers = ["12345", "abcdefg", "+1234567890123456"]
        for phone in invalid_phone_numbers:
            form_data = {"phone_number": phone}
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("phone_number", form.errors)

    def test_invalid_age(self):
        """Test invalid ages, including blank case."""
        invalid_ages = ["", 10, 150]  # Includes blank & out-of-range values
        for age in invalid_ages:
            form_data = {"age": age}
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("age", form.errors)

    def test_password_validation(self):
        """Test password validation rules."""
        invalid_passwords = ["short", "alllowercase", "ALLUPPERCASE", "NoNumbersHere"]
        for password in invalid_passwords:
            form_data = {
                "new_password": password,
                "confirm_password": password,
            }
            form = UserProfileForm(data=form_data, user=self.user)
            self.assertFalse(form.is_valid())
            self.assertIn("new_password", form.errors)

    def test_password_mismatch(self):
        """Test mismatching new password and confirm password."""
        form_data = {
            "new_password": "ValidPass123!",
            "confirm_password": "DifferentPass123!",
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_duplicate_email(self):
        """Test email uniqueness."""
        User.objects.create_user(username="otheruser", email="newemail@example.com", password="Test@1234")
        form_data = {"new_email": "newemail@example.com"}  # Already exists
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("new_email", form.errors)

    def test_password_with_spaces(self):
        """Test that passwords with spaces are invalid."""
        form_data = {
            "new_password": "With space1A",
            "confirm_password": "With space1A",
        }
        form = UserProfileForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("new_password", form.errors)
        self.assertTrue(any("Password should not contain spaces." in e for e in form.errors["new_password"]))

    def test_new_email_already_used_as_existing_email(self):
        """Test that an existing user's primary email is not allowed as new_email."""
        # Create another user who already uses this email as their main email
        User.objects.create_user(
            username="otheruser",
            email="used@example.com",
            password="Test@1234"
        )

        form_data = {
            "new_email": "used@example.com"
        }

        form = UserProfileForm(data=form_data, instance=self.end_user, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn("new_email", form.errors)

        self.assertTrue(
            any("user with this email already exists" in e.lower() for e in form.errors["new_email"]),
            "Expected error message about existing email not found."
        )

