from django.test import TestCase, Client
from django.urls import reverse
from client.models import Module
from users.models import User, EndUser, UserModuleEnrollment, UserModuleProgress
import csv
from django.conf import settings


class ExportModulesStatisticsCSVTest(TestCase):

    def setUp(self):
        """Set up test data for modules, users, and progress tracking."""
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            email="admin@example.com",
            is_superuser=True
        )


        # Create a regular (non-admin) user
        self.regular_user = User.objects.create_user(
            username="user1",
            password="password",
            email="user1@example.com",
            is_superuser=False
        )

        # Create modules
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.module3 = Module.objects.create(title="Module 3")

        # Create EndUsers associated with Users
        self.end_user1 = EndUser.objects.create(user=self.regular_user, age=25, gender='male', last_time_to_work='1_year', sector='it', phone_number="123456789")

        # Enroll the user in modules
        UserModuleEnrollment.objects.create(user=self.end_user1, module=self.module1)
        UserModuleEnrollment.objects.create(user=self.end_user1, module=self.module2)

        # Add progress data
        UserModuleProgress.objects.create(user=self.end_user1, module=self.module1, completion_percentage=75.0, status="in_progress")
        UserModuleProgress.objects.create(user=self.end_user1, module=self.module2, completion_percentage=85.0, status="completed")

        # Define URL for CSV export view
        self.url = reverse('export_modules_statistics_csv')

    def test_export_modules_statistics_csv_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_export_modules_statistics_csv_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_export_modules_statistics_csv_with_admin_access(self):
        """Test that an admin user can successfully export the CSV."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)

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
            ['Total Modules', '3'],  # Three modules created
            ['Enrollment - Module 1', '1'],  
            ['Enrollment - Module 2', '1'],  
            ['Enrollment - Module 3', '0'],  # No enrollment in Module 3
            ['Completion - Module 1 (Completed)', '0'],  # No 100% completion
            ['Completion - Module 1 (In Progress)', '1'],  # 75% in progress
            ['Completion - Module 2 (Completed)', '0'],  # 85% is still "in progress"
            ['Completion - Module 2 (In Progress)', '1'],  # 85% in progress
            ['Completion - Module 3 (Completed)', '0'],
            ['Completion - Module 3 (In Progress)', '0'],
            ['Avg Completion - Module 1', '75.0'],  # Average completion for Module 1
            ['Avg Completion - Module 2', '85.0'],  # Average completion for Module 2
            ['Avg Completion - Module 3', '0'],  # No progress in Module 3
            ['Avg Rating - Module 1', '0'],  
            ['Avg Rating - Module 2', '0'],  
            ['Avg Rating - Module 3', '0'],

        ]

        # Check if the generated CSV matches the expected output
        self.assertEqual(actual_csv, expected_csv)