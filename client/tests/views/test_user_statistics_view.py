import json
from django.test import TestCase
from django.urls import reverse
from users.models import EndUser, UserProgramEnrollment
from client.models import Program
from django.contrib.auth import get_user_model
from collections import Counter

User = get_user_model()

class UserStatisticsViewTest(TestCase):

    def setUp(self):
        """Set up test data for user statistics."""
        
        # Create users with UNIQUE emails
        self.user1 = User.objects.create_user(username="active_user", email="active@example.com", password="password", is_active=True)
        self.user2 = User.objects.create_user(username="inactive_user", email="inactive@example.com", password="password", is_active=False)

        # Create EndUsers with gender, ethnicity, and sector
        self.enduser1 = EndUser.objects.create(user=self.user1, gender="male", ethnicity="asian", sector="it")
        self.enduser2 = EndUser.objects.create(user=self.user2, gender="female", ethnicity="hispanic", sector="healthcare")

        # Create a Program BEFORE Enrolling Users
        self.program = Program.objects.create(title="Test Program", description="Sample Program")

        # Create a program enrollment (assign program_id properly)
        self.program_enrollment = UserProgramEnrollment.objects.create(user=self.enduser1, program=self.program)

        # Use the correct URL name
        self.url = reverse("userStatistics")  

        # Log in as `user1`
        self.client.login(username="active_user", password="password")


    def test_user_statistics_view_status_code(self):
        """Test if the user statistics page loads successfully."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_user_statistics_template_used(self):
        """Test that the correct template is used."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "client/userStatistics.html")


    def test_user_statistics_context_data(self):
        """Test that the context contains the correct user statistics."""
        response = self.client.get(self.url)


        #Ensure 'stats' exists
        self.assertIn("stats", response.context, "❌ 'stats' is missing in response context")

        # Ensure 'stats' is not None
        self.assertIsNotNone(response.context["stats"], "❌ 'stats' should not be None")

  
        try:
            stats_data = json.loads(response.context["stats"])
        except json.JSONDecodeError:
            self.fail("Response context 'stats' is not valid JSON")

        # Expected statistics
        expected_stats = {
            "total_users": 2,
            "active_users": 1,
            "inactive_users": 1,
            "programs_enrolled": 1,
            "gender_distribution": dict(Counter(["male", "female"])),
            "ethnicity_distribution": dict(Counter(["asian", "hispanic"])),
            "sector_distribution": dict(Counter(["it", "healthcare"])),
        }

        self.assertEqual(stats_data, expected_stats)
        

    def test_user_statistics_json_structure(self):
        """Ensure the JSON structure is valid."""
        response = self.client.get(self.url)
        self.assertIn("stats", response.context)

        try:
            json_data = json.loads(response.context["stats"])
            self.assertIsInstance(json_data, dict) 
        except json.JSONDecodeError:
            self.fail("Response context 'stats' is not valid JSON")
