from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from users.models import EndUser
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class ClientDashboardViewTest(TestCase):
    def setUp(self):
        """Set up an admin user for authentication."""
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True
        )

    @patch("client.statistics.get_module_enrollment_stats")
    @patch("client.statistics.get_users_last_work_time")
    def test_client_dashboard_view_authenticated(self, mock_last_work_time, mock_enrollment_stats):
        """Test that the dashboard loads for an authenticated admin user."""
        self.client.login(username="admin", password="adminpass")

        # Mock return values
        mock_enrollment_stats.return_value = (["Module A"], [10])
        mock_last_work_time.return_value = (["Last Week"], [5])

        # Create EndUser instances
        user1 = User.objects.create_user(username="user1", password="testpass", email="user1@example.com")
        user2 = User.objects.create_user(username="user2", password="testpass", email="user2@example.com")
        
        EndUser.objects.create(user=user1, age=25, gender="female", sector="healthcare")
        EndUser.objects.create(user=user2, age=30, gender="male", sector="it")

        response = self.client.get(reverse("client_dashboard"))

        # Ensure response is successful
        self.assertEqual(response.status_code, 200)
        
        # Ensure correct user count
        self.assertIn("users_count", response.context)
        self.assertEqual(response.context["users_count"], EndUser.objects.count())

        # Ensure statistics are in context
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("enrollment_data", response.context)
        self.assertIn("last_work_time_labels", response.context)
        self.assertIn("last_work_time_data", response.context)

    def test_client_dashboard_view_unauthenticated(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse("client_dashboard"))
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={reverse('client_dashboard')}")

    def test_client_dashboard_view_non_admin_user(self):
        """Test that a non-admin user is redirected to the login page."""
        regular_user = User.objects.create_user(username="user2", password="testpass", email="user2@example.com", is_staff=False)
        self.client.login(username="user2", password="testpass")

        response = self.client.get(reverse("client_dashboard"))

        # Expect a redirect (302) instead of 403
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

