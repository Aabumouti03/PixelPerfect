from django.test import TestCase, Client
from unittest.mock import patch
from django.urls import reverse

class StatisticsViewsTests(TestCase):

    @patch("client.modules_statistics.get_module_enrollment_stats")
    @patch("client.modules_statistics.get_users_last_work_time")
    @patch("client.programs_statistics.get_program_enrollment_stats")
    def test_reports_view(self, mock_program_enrollment, mock_last_work, mock_module_enrollment):
        mock_module_enrollment.return_value = (["Module A"], [5])
        mock_last_work.return_value = (["Last Week"], [10])
        mock_program_enrollment.return_value = (["Program A"], [3])

        response = self.client.get(reverse("reports"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("last_work_labels", response.context)
        self.assertIn("program_labels", response.context)

    @patch("client.modules_statistics.get_module_enrollment_stats")
    @patch("client.modules_statistics.get_module_completion_stats")
    @patch("client.modules_statistics.get_average_completion_percentage")
    @patch("client.modules_statistics.get_modules_count")
    def test_modules_statistics_view(self, mock_modules_count, mock_avg_completion, mock_completion_stats, mock_enrollment):
        mock_enrollment.return_value = (["Module A"], [5])
        mock_completion_stats.return_value = (["Module A"], [2], [3])
        mock_avg_completion.return_value = (["Module A"], [80])
        mock_modules_count.return_value = 1

        response = self.client.get(reverse("modules_statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("modules_count", response.context)
        self.assertIn("enrollment_labels", response.context)
        self.assertIn("completion_labels", response.context)

    @patch("client.programs_statistics.get_program_enrollment_stats")
    @patch("client.programs_statistics.get_program_completion_stats")
    @patch("client.programs_statistics.get_average_program_completion_percentage")
    @patch("client.programs_statistics.get_programs_count")
    def test_programs_statistics_view(self, mock_programs_count, mock_avg_completion, mock_completion_stats, mock_enrollment):
        mock_enrollment.return_value = (["Program A"], [3])
        mock_completion_stats.return_value = (["Program A"], [1], [2])
        mock_avg_completion.return_value = (["Program A"], [75])
        mock_programs_count.return_value = 1

        response = self.client.get(reverse("programs_statistics"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("programs_count", response.context)
        self.assertIn("program_labels", response.context)
        self.assertIn("completion_labels", response.context)
