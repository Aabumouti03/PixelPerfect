from django.test import TestCase
from unittest.mock import patch
from django.db.models import Avg, Count

from users.models import EndUser, UserProgramEnrollment, UserProgramProgress
from client.models import Program
from client.programs_statistics import (
    get_program_enrollment_stats,
    get_program_completion_stats,
    get_average_program_completion_percentage,
    get_programs_count,
)

class ProgramStatisticsTests(TestCase):
    
    @patch("client.models.Program.objects.values_list")
    @patch("users.models.UserProgramEnrollment.objects.values")
    def test_get_program_enrollment_stats(self, mock_enrollment_values, mock_program_values_list):
        mock_program_values_list.return_value = [(1, "Program A"), (2, "Program B")]
        mock_enrollment_values.return_value.annotate.return_value = [
            {"program__id": 1, "program__title": "Program A", "count": 5},
            {"program__id": 2, "program__title": "Program B", "count": 3},
        ]
        
        labels, data = get_program_enrollment_stats()
        self.assertEqual(labels, ["Program A", "Program B"])
        self.assertEqual(data, [5, 3])

    @patch("client.models.Program.objects.values_list")
    @patch("users.models.UserProgramProgress.objects.values")
    def test_get_program_completion_stats(self, mock_progress_values, mock_program_values_list):
        mock_program_values_list.return_value = ["Program A", "Program B"]
        mock_progress_values.return_value.annotate.return_value = [
            {"program__title": "Program A", "status": "completed", "count": 4},
            {"program__title": "Program A", "status": "in_progress", "count": 2},
            {"program__title": "Program B", "status": "completed", "count": 3},
        ]
        
        labels, completed_data, in_progress_data = get_program_completion_stats()
        self.assertEqual(labels, ["Program A", "Program B"])
        self.assertEqual(completed_data, [4, 3])
        self.assertEqual(in_progress_data, [2, 0])

    @patch("client.models.Program.objects.values_list")
    @patch("users.models.UserProgramProgress.objects.values")
    def test_get_average_program_completion_percentage(self, mock_completion_values, mock_program_values_list):
        mock_program_values_list.return_value = ["Program A", "Program B"]
        mock_completion_values.return_value.annotate.return_value = [
            {"program__title": "Program A", "avg_completion": 80.5},
            {"program__title": "Program B", "avg_completion": 65.2},
        ]
        
        labels, data = get_average_program_completion_percentage()
        self.assertEqual(labels, ["Program A", "Program B"])
        self.assertEqual(data, [80.5, 65.2])
    
    @patch("client.models.Program.objects.count")
    def test_get_programs_count(self, mock_programs_count):
        mock_programs_count.return_value = 2
        self.assertEqual(get_programs_count(), 2)
