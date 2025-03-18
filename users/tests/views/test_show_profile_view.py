from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, resolve
from users.models import EndUser
from django.contrib.messages import get_messages
from users.views import show_profile  # Importing the view for URL resolution test

User = get_user_model()

class ShowProfileViewTest(TestCase):
    def setUp(self):
        """Set up a test user, associated EndUser, and authenticate them using force_login."""
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
            sector="IT"
        )

        self.client.force_login(self.user)  #  Authenticated instantly

        self.profile_url = reverse("show_profile")  #  Ensure this matches your actual URL pattern


    def test_show_profile_authenticated_user(self):
        """Ensure the profile page loads correctly for an authenticated user."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User")  #  Check if the name appears on the profile page


    def test_redirect_if_not_logged_in(self):
        """Ensure unauthenticated users are redirected to the login page."""
        self.client.logout()  #  Simulate a logged-out user
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"/log_in/?next={self.profile_url}")  #  Ensure correct redirection


    def test_show_profile_url_resolves(self):
        """Test if the URL correctly resolves to the show_profile view."""
        found = resolve(self.profile_url)
        self.assertEqual(found.func, show_profile)


    def test_redirect_if_no_user_profile(self):
        """Test that users without a User_profile are redirected with an error."""
        self.client.login(username="testuser", password="Test@1234")

        # Delete the EndUser profile
        self.end_user.delete()

        response = self.client.get(self.profile_url)
        self.assertRedirects(response, reverse("welcome_page"))

        # Check error message is set
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "User profile not found.")


    def test_profile_update_popup_displayed(self):
        """Test that the email update pop-up appears after email verification."""

        # Set session data
        session = self.client.session
        session["profile_update_popup"] = "profile_updated"  # Must match the template condition
        session.save()

        # Fetch the profile page
        response = self.client.get(self.profile_url)

        # Assert the message is in the response
        self.assertContains(response, "Your email was successfully updated!")


    def test_partial_data_display(self):
        """Test that the profile page still loads with partial user data."""
        self.client.login(username="testuser", password="Test@1234")
        self.user.first_name = ""
        self.user.save()
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User")  # Ensures the last name is still displayed


    def test_edge_case_empty_name(self):
        """Test validation for missing first and last name."""
        self.client.login(username="testuser", password="Test@1234")
        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save()
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "N/A")  # Ensure fallback behavior
