from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse
from users.models import User
from django.conf import settings

class StatisticsViewsTests(TestCase):

    def setUp(self):
        """Set up test users for authentication tests."""
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_superuser=True
        )

        # Create a regular (non-admin) user
        self.regular_user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="userpass",
            is_superuser=False
        )

    def test_reports_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_reports_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    @patch("client.statistics.get_module_enrollment_stats")
    @patch("client.statistics.get_users_last_work_time")
    @patch("client.statistics.get_program_enrollment_stats")
    def test_reports_view_admin_access(self, mock_program_enrollment, mock_last_work, mock_module_enrollment):
        """Test that an admin user can access the reports view."""
        self.client.login(username="admin", password="adminpass")

        mock_module_enrollment.return_value = (["Module A"], [5])
        mock_last_work.return_value = (["Last Week"], [10])
        mock_program_enrollment.return_value = (["Program A"], [3])

        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("last_work_labels", response.context)
        self.assertIn("program_labels", response.context)

    def test_modules_statistics_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse("modules_statistics"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_modules_statistics_requires_admin(self):
        """Test that a non-admin user gets a 302 log in -> Forbidden error."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    @patch("client.statistics.get_module_enrollment_stats")
    @patch("client.statistics.get_module_completion_stats")
    @patch("client.statistics.get_average_completion_percentage")
    @patch("client.statistics.get_modules_count")
    def test_modules_statistics_view_admin_access(self, mock_modules_count, mock_avg_completion, mock_completion_stats, mock_enrollment):
        """Test that an admin user can access the modules statistics view."""
        self.client.login(username="admin", password="adminpass")

        mock_enrollment.return_value = (["Module A"], [5])
        mock_completion_stats.return_value = (["Module A"], [2], [3])
        mock_avg_completion.return_value = (["Module A"], [80])
        mock_modules_count.return_value = 1

        response = self.client.get(reverse("modules_statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("modules_count", response.context)
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("completion_labels", response.context)

    def test_programs_statistics_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse("programs_statistics"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_programs_statistics_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(reverse("programs_statistics"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    @patch("client.statistics.get_program_enrollment_stats")
    @patch("client.statistics.get_program_completion_stats")
    @patch("client.statistics.get_average_program_completion_percentage")
    @patch("client.statistics.get_programs_count")
    def test_programs_statistics_view_admin_access(self, mock_programs_count, mock_avg_completion, mock_completion_stats, mock_enrollment):
        """Test that an admin user can access the programs statistics view."""
        self.client.login(username="admin", password="adminpass")

        mock_enrollment.return_value = (["Program A"], [3])
        mock_completion_stats.return_value = (["Program A"], [1], [2])
        mock_avg_completion.return_value = (["Program A"], [75])
        mock_programs_count.return_value = 1

        response = self.client.get(reverse("programs_statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("programs_count", response.context)
        self.assertIn("program_labels", response.context)
        self.assertIn("completion_labels", response.context)
