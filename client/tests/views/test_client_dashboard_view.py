from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse

class ClientDashboardViewTest(TestCase):

    @patch("client.modules_statistics.get_module_enrollment_stats")
    @patch("client.modules_statistics.get_users_last_work_time")
    def test_client_dashboard_view(self, mock_last_work_time, mock_enrollment_stats):
        mock_enrollment_stats.return_value = (["Module A"], [10])
        mock_last_work_time.return_value = (["Last Week"], [5])
        
        response = self.client.get(reverse("client_dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("enrollment_data", response.context)
        self.assertIn("last_work_time_labels", response.context)
        self.assertIn("last_work_time_data", response.context)
