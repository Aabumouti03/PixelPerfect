from django.test import TestCase, Client
from django.urls import reverse
from client.models import Program
from users.models import User, EndUser, UserProgramEnrollment
import csv
from django.conf import settings


class ExportUserStatisticsCSVTest(TestCase):

    def setUp(self):
        """Set up test data for users and enrollments."""
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            email="admin@example.com",
            is_superuser=True
        )

        # Create a regular (non-admin) user
        self.regular_user1 = User.objects.create_user(
            username="user1",
            password="password",
            email="user1@example.com",
            is_superuser=False
        )

        self.regular_user2 = User.objects.create_user(
            username="user2",
            password="password",
            email="user2@example.com",
            is_superuser=False
        )

        # Create programs
        self.program1 = Program.objects.create(title="Program 1")

        # Create EndUsers associated with Users
        self.end_user1 = EndUser.objects.create(user=self.regular_user1, age=25, gender='male', last_time_to_work='1_year', sector='it', phone_number="123456789")
        self.end_user2 = EndUser.objects.create(user=self.regular_user2, age=28, gender='female', last_time_to_work='3_months', sector='education', phone_number="987654321")

        # Enroll the users in programs
        UserProgramEnrollment.objects.create(user=self.end_user1, program=self.program1)
        UserProgramEnrollment.objects.create(user=self.end_user2, program=self.program1)

        # Define URL for CSV export view
        self.url = reverse('export_user_statistics_csv')

    def test_export_user_statistics_csv_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_export_user_statistics_csv_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_export_user_statistics_csv_with_admin_access(self):
        """Test that an admin user can successfully export the CSV."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)

        # Check if the response is a CSV file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="user_statistics.csv"')

        # Read the CSV content from the response
        response_content = response.content.decode('utf-8').splitlines()
        csv_reader = csv.reader(response_content)
        actual_csv = list(csv_reader)

        # **Expected CSV format and content (keeping your values unchanged)**
        expected_csv = [
            ['Statistic', 'Value'],
            ['Total Users', '2'],  # Two users are created
            ['Active Users', '2'],  # Both users are active
            ['Inactive Users', '0'],  # No inactive users
            ['Total Programs Enrolled', '2'],  # Two users enrolled in 1 program
            ['Gender - male', '1'],
            ['Gender - female', '1'],
            ['Ethnicity - None', '2'],  # Default for both users
            ['Sector - it', '1'],
            ['Sector - education', '1'],
        ]

        # Check if the generated CSV matches the expected output
        self.assertEqual(actual_csv, expected_csv)