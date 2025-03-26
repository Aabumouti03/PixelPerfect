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

        self.admin_user = User.objects.create_superuser(
            username="admin_user", email="admin@example.com", password="adminpassword"
        )

        # ✅ Create a normal user (should NOT have access)
        self.user = User.objects.create_user(
            username="normal_user", email="user@example.com", password="password"
        )

        # ✅ Create EndUsers
        self.enduser1 = EndUser.objects.create(user=self.admin_user, gender="male", ethnicity="asian", sector="it")
        self.enduser2 = EndUser.objects.create(user=self.user, gender="female", ethnicity="hispanic", sector="healthcare")

        # ✅ Create a Program and enroll a user
        self.program = Program.objects.create(title="Test Program", description="Sample Program")
        UserProgramEnrollment.objects.create(user=self.enduser1, program=self.program)

        # ✅ Define the correct URL
        self.url = reverse("userStatistics")


    def test_user_statistics_view_status_code(self):
        """Test if the user statistics page loads successfully for an admin."""
        self.client.login(username="admin_user", password="adminpassword")  # ✅ Log in as admin
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # ✅ Expecting success


    def test_redirect_for_non_admin(self):
        """Ensure non-admin users are redirected (permission check)."""
        self.client.login(username="normal_user", password="password")  # ✅ Log in as normal user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # ✅ Should redirect


    def test_user_statistics_template_used(self):
        """Test that the correct template is used."""
        self.client.login(username="admin_user", password="adminpassword")  # ✅ Log in as admin
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "client/userStatistics.html")


    def test_user_statistics_context_data(self):
        """Test that the context contains the correct user statistics."""
        self.client.login(username="admin_user", password="adminpassword")  # ✅ Log in as admin
        response = self.client.get(self.url)

        # ✅ Ensure 'stats' exists in the context
        self.assertIn("stats", response.context, "❌ 'stats' is missing in response context")

        # ✅ Ensure 'stats' is valid JSON
        stats_data = json.loads(response.context["stats"])

        # ✅ Retrieve actual database counts
        actual_total_users = EndUser.objects.count()
        actual_active_users = EndUser.objects.filter(user__is_active=True).count()
        actual_inactive_users = actual_total_users - actual_active_users
        actual_programs_enrolled = UserProgramEnrollment.objects.count()

        # ✅ Expected statistics
        expected_stats = {
            "total_users": actual_total_users,
            "active_users": actual_active_users,
            "inactive_users": actual_inactive_users,
            "programs_enrolled": actual_programs_enrolled,
            "gender_distribution": dict(Counter(EndUser.objects.values_list('gender', flat=True))),
            "ethnicity_distribution": dict(Counter(EndUser.objects.values_list('ethnicity', flat=True))),
            "sector_distribution": dict(Counter(EndUser.objects.values_list('sector', flat=True))),
        }

        # ✅ Compare actual and expected results
        self.assertEqual(stats_data, expected_stats, "❌ Mismatch between expected and actual user statistics!")


    def test_user_statistics_json_structure(self):
        """Ensure the JSON structure is valid."""
        self.client.login(username="admin_user", password="adminpassword")  # ✅ Log in as admin
        response = self.client.get(self.url)

        self.assertIn("stats", response.context, "❌ 'stats' is missing in response context")

        
        json_data = json.loads(response.context["stats"])
        self.assertIsInstance(json_data, dict)  # ✅ Ensure it's a dictionary
        self.assertIn("total_users", json_data)
        self.assertIn("active_users", json_data)
        self.assertIn("inactive_users", json_data)
        self.assertIn("programs_enrolled", json_data)
        self.assertIn("gender_distribution", json_data)
        self.assertIn("ethnicity_distribution", json_data)
        self.assertIn("sector_distribution", json_data)
    
    def test_statistics_with_no_users_or_enrollments(self):
        EndUser.objects.exclude(user=self.admin_user).delete()
        UserProgramEnrollment.objects.all().delete()

        self.client.login(username="admin_user", password="adminpassword")
        response = self.client.get(self.url)
        stats_data = json.loads(response.context["stats"])

        expected_stats = {
            "total_users": 1,
            "active_users": 1,
            "inactive_users": 0,
            "programs_enrolled": 0,
            "gender_distribution": {"male": 1},
            "ethnicity_distribution": {"asian": 1},
            "sector_distribution": {"it": 1},
        }

        self.assertEqual(stats_data, expected_stats)

    def test_redirect_for_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in", response.url)
