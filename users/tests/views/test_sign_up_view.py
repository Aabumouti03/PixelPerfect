from django.test import TestCase
from django.urls import reverse
from users.models import User, EndUser
from users.forms import UserSignUpForm, EndUserProfileForm

class SignUpViewTestCase(TestCase):
    """Unit tests for the sign-up process (step 1 and step 2)."""

    def setUp(self):
        """Set up the sign-up URLs and test user data."""
        self.sign_up_step_1_url = reverse("sign_up_step_1")
        self.sign_up_step_2_url = reverse("sign_up_step_2")
        self.log_in_url = reverse("log_in")

        self.valid_user_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "TestUser123!",
            "password2": "TestUser123!",
        }

        self.valid_profile_data = {
            "age": 25,
            "gender": "male",
            "sector": "it",
            "ethnicity": "asian",
            "last_time_to_work": "1_year",
            "phone_number": "+1234567890",
        }

    # --- Step 1 Tests ---

    def test_get_sign_up_step_1_page(self):
        """Ensure the sign-up step 1 page loads successfully."""
        response = self.client.get(self.sign_up_step_1_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_1.html")
        self.assertIsInstance(response.context["user_form"], UserSignUpForm)

    def test_post_valid_sign_up_step_1_redirects_to_step_2(self):
        """Ensure valid user details in step 1 redirect to step 2."""
        response = self.client.post(self.sign_up_step_1_url, self.valid_user_data, follow=True)
        self.assertRedirects(response, self.sign_up_step_2_url)
        self.assertIn("user_form_data", self.client.session)

    def test_post_invalid_sign_up_step_1_shows_errors(self):
        """Ensure invalid user details in step 1 show form errors."""
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = ""  # Missing email
        response = self.client.post(self.sign_up_step_1_url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_1.html")
        self.assertIn("user_form", response.context)
        self.assertTrue(response.context["user_form"].errors)
        self.assertIn("email", response.context["user_form"].errors)

    # --- Step 2 Tests ---

    def test_get_sign_up_step_2_without_step_1_redirects_to_step_1(self):
        """Ensure users cannot access step 2 without completing step 1."""
        response = self.client.get(self.sign_up_step_2_url, follow=True)
        self.assertRedirects(response, self.sign_up_step_1_url)

    def test_get_sign_up_step_2_after_step_1(self):
        """Ensure users can access step 2 only after step 1 is completed."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data  # Simulate step 1 completion
        session.save()

        response = self.client.get(self.sign_up_step_2_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_2.html")
        self.assertIsInstance(response.context["profile_form"], EndUserProfileForm)

    def test_post_valid_sign_up_step_2_creates_user_and_redirects_to_login(self):
        """Ensure completing step 2 creates a user and redirects to login."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data  # Simulate step 1 completion
        session.save()

        response = self.client.post(self.sign_up_step_2_url, self.valid_profile_data, follow=True)

        self.assertRedirects(response, self.log_in_url)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(EndUser.objects.filter(user__username="testuser").exists())

    def test_post_invalid_sign_up_step_2_shows_errors(self):
        """Ensure invalid profile details in step 2 show form errors."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()

        invalid_profile_data = self.valid_profile_data.copy()
        invalid_profile_data["age"] = 15  # Invalid age (too young)

        response = self.client.post(self.sign_up_step_2_url, invalid_profile_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_2.html")
        self.assertTrue(response.context["profile_form"].errors)
        self.assertIn("age", response.context["profile_form"].errors)
