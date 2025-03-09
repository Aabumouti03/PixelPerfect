from django.test import TestCase
from django.urls import reverse
from client.models import Module, Program
from users.models import User, EndUser, UserModuleEnrollment, UserModuleProgress
import csv

class ExportModulesStatisticsCSVTest(TestCase):

    def setUp(self):
        # Create real modules and programs
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.module3 = Module.objects.create(title="Module 3")

        # Create a user and associate with the program and modules
        self.user1 = User.objects.create_user(username="user1", password="password", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", password="password", email="user2@example.com")

        self.end_user1 = EndUser.objects.create(user=self.user1, age=25, gender='male', last_time_to_work='1_year', sector='it', phone_number="123456789")
        self.end_user2 = EndUser.objects.create(user=self.user2, age=28, gender='female', last_time_to_work='3_months', sector='education', phone_number="987654321")

        # Enroll the users into programs and modules
        self.enrollment2 = UserModuleEnrollment.objects.create(user=self.end_user1, module=self.module1)
        self.enrollment3 = UserModuleEnrollment.objects.create(user=self.end_user2, module=self.module2)
        self.enrollment4 = UserModuleEnrollment.objects.create(user=self.end_user2, module=self.module3)

        # Add progress data
        self.progress2 = UserModuleProgress.objects.create(user=self.end_user1, module=self.module1, completion_percentage=75.0, status="in_progress")
        self.progress2 = UserModuleProgress.objects.create(user=self.end_user2, module=self.module1, completion_percentage=0.0, status="completed")
        self.progress3 = UserModuleProgress.objects.create(user=self.end_user2, module=self.module2, completion_percentage=85.0, status="completed")

    def test_export_modules_statistics_csv_with_real_modules(self):
        # URL for the view
        url = reverse('export_modules_statistics_csv')

        # Send GET request to the view
        response = self.client.get(url)

        # Check if the response is a CSV file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="modules_statistics.csv"')

        # Read the CSV content from the response
        response_content = response.content.decode('utf-8').splitlines()
        csv_reader = csv.reader(response_content)
        actual_csv = list(csv_reader)

        # Define expected CSV format and content
        expected_csv = [
            ['Statistic', 'Value'],
            ['Total Modules', '3'],  # As we created 3 modules
            ['Enrollment - Module 1', '1'],  # Assuming the enrollment data from your models
            ['Enrollment - Module 2', '1'],  
            ['Enrollment - Module 3', '1'],
            ['Completion - Module 1 (Completed)', '1'],
            ['Completion - Module 1 (In Progress)', '1'],
            ['Completion - Module 2 (Completed)', '1'],
            ['Completion - Module 2 (In Progress)', '0'],
            ['Completion - Module 3 (Completed)', '0'],
            ['Completion - Module 3 (In Progress)', '0'],
            ['Avg Completion - Module 1', '37.5'],  # Average completion for Module 1
            ['Avg Completion - Module 2', '85.0'],  # Average completion for Module 2
            ['Avg Completion - Module 3', '0'],  # Average completion for Module 3
        ]

        # Check if the generated CSV matches the expected output
        self.assertEqual(actual_csv, expected_csv)
