from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from users.models import EndUser

class ClientDashboardViewTest(TestCase):
    @patch("client.modules_statistics.get_module_enrollment_stats")
    @patch("client.modules_statistics.get_users_last_work_time")
    @patch("users.models.EndUser.objects.all")
    def test_client_dashboard_view(self, mock_users_count, mock_last_work_time, mock_enrollment_stats):
        mock_enrollment_stats.return_value = (["Module A"], [10])
        mock_last_work_time.return_value = (["Last Week"], [5])
        mock_users_count.return_value = [1, 2, 3]  # Simulating 3 users
        
        response = self.client.get(reverse("client_dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("users_count", response.context)
        self.assertEqual(response.context["users_count"], 3)  # Ensuring user count is passed correctly
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("enrollment_data", response.context)
        self.assertIn("last_work_time_labels", response.context)
        self.assertIn("last_work_time_data", response.context)
