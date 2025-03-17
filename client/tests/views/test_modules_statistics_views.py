from django.test import TestCase
from unittest.mock import patch
from django.db.models import Avg, Count
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module
from users.models import EndUser
from django.test.client import Client


from client.statistics import (
    get_module_enrollment_stats,
    get_module_completion_stats,
    get_average_completion_percentage,
    get_modules_count,
    get_users_last_work_time,
)

class ModuleStatisticsTests(TestCase):
    
    @patch("client.models.Module.objects.values_list")
    @patch("users.models.UserModuleEnrollment.objects.values")
    def test_get_module_enrollment_stats(self, mock_enrollment_values, mock_module_values_list):
        mock_module_values_list.return_value = [(1, "Module A"), (2, "Module B")]
        mock_enrollment_values.return_value.annotate.return_value = [
            {"module__id": 1, "module__title": "Module A", "count": 5},
            {"module__id": 2, "module__title": "Module B", "count": 3},
        ]
        
        labels, data = get_module_enrollment_stats()
        self.assertEqual(labels, ["Module A", "Module B"])
        self.assertEqual(data, [5, 3])

    @patch("client.models.Module.objects.values_list")
    @patch("users.models.UserModuleProgress.objects.values")
    def test_get_module_completion_stats(self, mock_progress_values, mock_module_values_list):
        mock_module_values_list.return_value = ["Module A", "Module B"]
        mock_progress_values.return_value.annotate.return_value = [
            {"module__title": "Module A", "status": "completed", "count": 4},
            {"module__title": "Module A", "status": "in_progress", "count": 2},
            {"module__title": "Module B", "status": "completed", "count": 3},
        ]
        
        labels, completed_data, in_progress_data = get_module_completion_stats()
        self.assertEqual(labels, ["Module A", "Module B"])
        self.assertEqual(completed_data, [4, 3])
        self.assertEqual(in_progress_data, [2, 0])

    @patch("client.models.Module.objects.values_list")
    @patch("users.models.UserModuleProgress.objects.values")
    def test_get_average_completion_percentage(self, mock_completion_values, mock_module_values_list):
        mock_module_values_list.return_value = ["Module A", "Module B"]
        mock_completion_values.return_value.annotate.return_value = [
            {"module__title": "Module A", "avg_completion": 80.5},
            {"module__title": "Module B", "avg_completion": 65.2},
        ]
        
        labels, data = get_average_completion_percentage()
        self.assertEqual(labels, ["Module A", "Module B"])
        self.assertEqual(data, [80.5, 65.2])
    
    @patch("client.models.Module.objects.all")
    def test_get_modules_count(self, mock_modules_all):
        mock_modules_all.return_value.values.return_value = [{"title": "Module A"}, {"title": "Module B"}]
        self.assertEqual(get_modules_count(), 2)

    @patch("users.models.EndUser.objects.values")
    def test_get_users_last_work_time(self, mock_enduser_values):
        mock_enduser_values.return_value.annotate.return_value.order_by.return_value = [
            {"last_time_to_work": "1_month", "count": 10},
            {"last_time_to_work": "3_months", "count": 5},
        ]
        
        labels, data = get_users_last_work_time()
        self.assertEqual(labels, ["1_month", "3_months"])
        self.assertEqual(data, [10, 5])




#Testing the ratings
User = get_user_model()

class ModuleRatingsTests(TestCase):

    def setUp(self):
        """Set up a test user and log them in as an admin."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpassword")
        self.client = Client()
        self.client.login(username="admin", password="adminpassword")  # Log in as admin

    @patch("client.models.Module.objects.annotate")
    @patch("client.statistics.get_module_enrollment_stats")
    @patch("client.statistics.get_module_completion_stats")
    @patch("client.statistics.get_average_completion_percentage")
    @patch("client.statistics.get_modules_count")

    def test_modules_statistics_view_ratings(
        self, 
        mock_modules_count, 
        mock_avg_completion, 
        mock_completion_stats, 
        mock_enrollment_stats,
        mock_module_annotate
    ):
     
        
        # Mock statistics data
        mock_modules_count.return_value = 2
        mock_enrollment_stats.return_value = (["Module A", "Module B"], [10, 5])
        mock_completion_stats.return_value = (["Module A", "Module B"], [8, 3], [2, 2])
        mock_avg_completion.return_value = (["Module A", "Module B"], [85.5, 72.3])

        # Mock average ratings for modules
        mock_module_annotate.return_value.values.return_value = [
            {"title": "Module A", "avg_rating": 4.2},
            {"title": "Module B", "avg_rating": 3.8},
        ]

        # Get the response from the view
        response = self.client.get(reverse("modules_statistics"))  # Ensure the correct URL name

        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)

        # Ensure the context contains the correct data
        context = response.context

        # Check if the average ratings are present
        self.assertIn("rating_labels", context)
        self.assertIn("rating_data", context)

        # Parse JSON data
        rating_labels = context["rating_labels"]
        rating_data = context["rating_data"]

        # Expected results
        expected_labels = '["Module A", "Module B"]'
        expected_data = '[4.2, 3.8]'

        # Assert correct rating values
        self.assertEqual(rating_labels, expected_labels)
        self.assertEqual(rating_data, expected_data)