from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser
 
User = get_user_model()

class StaticUserPageTests(TestCase):
    def setUp(self):
         self.user = User.objects.create_user(
             username="testuser",
             email="test@example.com",
             password="TestPass123",
             email_verified=True
         )
         EndUser.objects.create(user=self.user, age=25, gender="male", sector="it", last_time_to_work="1_month")
         self.client.login(username="testuser", password="TestPass123")

    def test_profile_view(self):
        """Should render the profile page successfully."""
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_welcome_view(self):
        """Should render the welcome page successfully."""
        response = self.client.get(reverse("welcome"))
        self.assertEqual(response.status_code, 200)

    def test_contact_success(self):
        """Should render the contact success page successfully."""
        response = self.client.get(reverse("contact_success"))
        self.assertEqual(response.status_code, 200)