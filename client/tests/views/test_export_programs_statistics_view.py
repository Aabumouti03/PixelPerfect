from django.test import TestCase
from django.urls import reverse
from client.models import Program, Module
from users.models import User, EndUser, UserProgramEnrollment, UserProgramProgress
import csv

class ExportProgramsStatisticsCSVTest(TestCase):

    def setUp(self):
        # Create real programs and modules
        self.program1 = Program.objects.create(title="Program 1")
        self.program2 = Program.objects.create(title="Program 2")
        self.program3 = Program.objects.create(title="Program 3")

        # Create a user and associate with the programs
        self.user1 = User.objects.create_user(username="user1", password="password", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", password="password", email="user2@example.com")

        self.end_user1 = EndUser.objects.create(user=self.user1, age=25, gender='male', last_time_to_work='1_year', sector='it', phone_number="123456789")
        self.end_user2 = EndUser.objects.create(user=self.user2, age=28, gender='female', last_time_to_work='3_months', sector='education', phone_number="987654321")

        # Enroll the users into programs
        self.enrollment1 = UserProgramEnrollment.objects.create(user=self.end_user1, program=self.program1)
        self.enrollment2 = UserProgramEnrollment.objects.create(user=self.end_user2, program=self.program2)
        self.enrollment3 = UserProgramEnrollment.objects.create(user=self.end_user2, program=self.program3)

        # Add progress data
        self.progress1 = UserProgramProgress.objects.create(user=self.end_user1, program=self.program1, completion_percentage=75.0, status="in_progress")
        self.progress2 = UserProgramProgress.objects.create(user=self.end_user2, program=self.program1, completion_percentage=0.0, status="completed")
        self.progress3 = UserProgramProgress.objects.create(user=self.end_user2, program=self.program2, completion_percentage=85.0, status="completed")

    def test_export_programs_statistics_csv_with_real_programs(self):
        # URL for the view
        url = reverse('export_programs_statistics_csv')

        # Send GET request to the view
        response = self.client.get(url)

        # Check if the response is a CSV file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="programs_statistics.csv"')

        # Read the CSV content from the response
        response_content = response.content.decode('utf-8').splitlines()
        csv_reader = csv.reader(response_content)
        actual_csv = list(csv_reader)

        # Define expected CSV format and content
        expected_csv = [
            ['Statistic', 'Value'],
            ['Total Programs', '3'],  # As we created 3 programs
            ['Enrollment - Program 1', '1'],  # 1 user enrolled in Program 1
            ['Enrollment - Program 2', '1'],  # 1 user enrolled in Program 2
            ['Enrollment - Program 3', '1'],  # 1 user enrolled in Program 3
            ['Completion - Program 1 (Completed)', '1'],  # 1 completed in Program 1
            ['Completion - Program 1 (In Progress)', '1'],  # 1 in progress in Program 1
            ['Completion - Program 2 (Completed)', '1'],  # 1 completed in Program 2
            ['Completion - Program 2 (In Progress)', '0'],  # 0 in progress in Program 2
            ['Completion - Program 3 (Completed)', '0'],  # 0 completed in Program 3
            ['Completion - Program 3 (In Progress)', '0'],  # 0 in progress in Program 3
            ['Avg Completion - Program 1', '37.5'],  # Average completion for Program 1
            ['Avg Completion - Program 2', '85.0'],  # Average completion for Program 2
            ['Avg Completion - Program 3', '0'],  # Average completion for Program 3 (no progress)
        ]

        # Check if the generated CSV matches the expected output
        self.assertEqual(actual_csv, expected_csv)
