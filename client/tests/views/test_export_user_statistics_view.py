from django.test import TestCase
from django.urls import reverse
from client.models import Program
from users.models import User, EndUser, UserProgramEnrollment
import csv

class ExportUserStatisticsCSVTest(TestCase):

    def setUp(self):
        # Create real users
        self.user1 = User.objects.create_user(username="user1", password="password", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", password="password", email="user2@example.com")

        # Create real programs (used for enrollment)
        self.program1 = Program.objects.create(title="Program 1")

        self.end_user1 = EndUser.objects.create(user=self.user1, age=25, gender='male', last_time_to_work='1_year', sector='it', phone_number="123456789")
        self.end_user2 = EndUser.objects.create(user=self.user2, age=28, gender='female', last_time_to_work='3_months', sector='education', phone_number="987654321")

        # Enroll the users into programs
        self.enrollment1 = UserProgramEnrollment.objects.create(user=self.end_user1, program=self.program1)
        self.enrollment2 = UserProgramEnrollment.objects.create(user=self.end_user2, program=self.program1)

    def test_export_user_statistics_csv(self):
        # URL for the view
        url = reverse('export_user_statistics_csv')

        # Send GET request to the view
        response = self.client.get(url)

        # Check if the response is a CSV file
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="user_statistics.csv"')

        # Read the CSV content from the response
        response_content = response.content.decode('utf-8').splitlines()
        csv_reader = csv.reader(response_content)
        actual_csv = list(csv_reader)

        # Define expected CSV format and content
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
