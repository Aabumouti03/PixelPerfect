from django.test import TestCase
from django.urls import reverse
from users.models import User, EndUser
from users.forms import UserSignUpForm, EndUserProfileForm

class SignUpViewTestCase(TestCase):
    """Unit tests for the sign-up process (step 1 and step 2)."""

    def setUp(self):
        self.sign_up_step_1_url = reverse("sign_up_step_1")
        self.sign_up_step_2_url = reverse("sign_up_step_2")
        self.questionnaire = reverse("questionnaire")

        self.valid_user_data = {
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        }


        self.valid_profile_data = {
            "age": 25,
            "gender": "male",
            "sector": "it",
            "ethnicity": "asian",
            "last_time_to_work": "1_year",
            "phone_number": "+1234567890",
        }

    def test_get_sign_up_step_1_page(self):
        response = self.client.get(self.sign_up_step_1_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_1.html")
        self.assertIsInstance(response.context["user_form"], UserSignUpForm)

    def test_post_valid_sign_up_step_1_redirects_to_step_2(self):
        """Ensure Step 1 submission redirects correctly to Step 2."""
        response = self.client.post(self.sign_up_step_1_url, self.valid_user_data)
        self.assertRedirects(response, self.sign_up_step_2_url)
        self.assertIn("user_form_data", self.client.session)

    def test_post_invalid_sign_up_step_1_shows_errors(self):
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = ""
        response = self.client.post(self.sign_up_step_1_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_1.html")
        self.assertTrue(response.context["user_form"].errors)
        self.assertIn("email", response.context["user_form"].errors)

    def test_get_sign_up_step_2_without_step_1_redirects_to_step_1(self):
        response = self.client.get(self.sign_up_step_2_url)
        self.assertRedirects(response, self.sign_up_step_1_url)

    def test_get_sign_up_step_2_after_step_1(self):
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()
        response = self.client.get(self.sign_up_step_2_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_2.html")
        self.assertIsInstance(response.context["profile_form"], EndUserProfileForm)

    def test_post_valid_sign_up_step_2_creates_user_and_redirects_to_login(self):
        """Ensure user and profile are created in Step 2 and redirect to login."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()

        response = self.client.post(self.sign_up_step_2_url, self.valid_profile_data, follow=True)
        self.assertRedirects(response, self.questionnaire)
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(EndUser.objects.filter(user__username="testuser").exists())

    def test_post_invalid_sign_up_step_2_shows_errors(self):
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()
        invalid_profile_data = self.valid_profile_data.copy()
        invalid_profile_data["age"] = "invalid_age"
        response = self.client.post(self.sign_up_step_2_url, invalid_profile_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_2.html")
        self.assertTrue(response.context["profile_form"].errors)
        self.assertIn("age", response.context["profile_form"].errors)

    def test_post_empty_sign_up_step_2_shows_errors(self):
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()
        response = self.client.post(self.sign_up_step_2_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_2.html")
        self.assertTrue(response.context["profile_form"].errors)

    def test_sign_up_step_1_duplicate_username_fails(self):
        """Ensure a duplicate username cannot be used in sign-up step 1."""
        User.objects.create_user(username="testuser", password="TestUser123!")

        duplicate_data = self.valid_user_data.copy()
        response = self.client.post(self.sign_up_step_1_url, duplicate_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/sign_up_step_1.html")

        form = response.context["user_form"]
        self.assertTrue(form.errors)
        self.assertIn("username", form.errors)

    def test_sign_up_step_1_does_not_create_user_in_db(self):
        """Ensure no user is created in the database after step 1 submission."""
        self.client.post(self.sign_up_step_1_url, self.valid_user_data)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_sign_up_step_1_prepopulates_data_from_session(self):
        """Ensure user form is pre-filled with session data when returning to Step 1."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()

        response = self.client.get(self.sign_up_step_1_url)
        self.assertEqual(response.status_code, 200)
        form = response.context["user_form"]

        self.assertEqual(form.initial["username"], "testuser")
        self.assertEqual(form.initial["email"], "test@example.com")

    def test_sign_up_step_2_fails_with_invalid_session_data(self):
        """Ensure step 2 fails gracefully when session user data is invalid."""
        session = self.client.session
        session["user_form_data"] = {"username": "", "password1": "123", "password2": "456"}
        session.save()

        response = self.client.post(self.sign_up_step_2_url, self.valid_profile_data)
        self.assertRedirects(response, self.sign_up_step_1_url)
    
    def test_profile_is_linked_to_correct_user(self):
        """Ensure the EndUser profile is correctly linked to the registered user."""
        session = self.client.session
        session["user_form_data"] = self.valid_user_data
        session.save()

        self.client.post(self.sign_up_step_2_url, self.valid_profile_data)

        user = User.objects.filter(username="testuser").first()
        self.assertIsNotNone(user, "User was not created")

        profile = EndUser.objects.filter(user=user).first()
        self.assertIsNotNone(profile, "Profile was not created")
        self.assertEqual(profile.phone_number, self.valid_profile_data["phone_number"])
        self.assertEqual(profile.age, self.valid_profile_data["age"])



