from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire
from users.models import  Questionnaire_UserResponse, EndUser
from django.utils.timezone import now
from datetime import timedelta

User = get_user_model()


class ManageQuestionnairesTest(TestCase):
    """Test suite for manage_questionnaires view"""

    def setUp(self):
        """Create test users and sample data"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )
        self.end_user = EndUser.objects.create(user=self.normal_user, age=30, gender="male", sector="it")

        self.q1 = Questionnaire.objects.create(
        title="Workplace Confidence Survey", is_active=True, created_at=now() - timedelta(days=3)
        )
        self.q2 = Questionnaire.objects.create(
            title="Job Readiness Assessment", is_active=False, created_at=now() - timedelta(days=2)
        )
        self.q3 = Questionnaire.objects.create(
            title="Returning to Work Survey", is_active=True, created_at=now() - timedelta(days=1)
        )

        Questionnaire_UserResponse.objects.create(questionnaire=self.q1, user=self.end_user)
        Questionnaire_UserResponse.objects.create(questionnaire=self.q2, user=self.end_user)
        
    def test_redirect_if_not_logged_in(self):
        """Test that non-authenticated users are redirected"""
        response = self.client.get(reverse("manage_questionnaires"))
        expected_url = reverse("log_in") + "?next=" + reverse("manage_questionnaires")
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that normal users are redirected instead of getting a 403"""
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("manage_questionnaires"))

        expected_url = reverse("log_in") + "?next=" + reverse("manage_questionnaires")
        self.assertRedirects(response, expected_url)


    def test_admin_can_access_page(self):
        """Test that an admin can access the page"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/Manage_Questionnaires.html")

    def test_search_functionality(self):
        """Test that search filters questionnaires correctly"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"), {"search": "Workplace"})
        self.assertContains(response, "Workplace Confidence Survey")
        self.assertNotContains(response, "Job Readiness Assessment")

    def test_filter_active_questionnaires(self):
        """Test filtering active questionnaires"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"), {"is_active": "true"})
        self.assertContains(response, "Workplace Confidence Survey")
        self.assertContains(response, "Returning to Work Survey")
        self.assertNotContains(response, "Job Readiness Assessment")

    def test_pagination(self):
        """Test that pagination works correctly"""
        self.client.login(username="admin", password="adminpass")

        # Create 12 more questionnaires (total = 15)
        for i in range(12):
            Questionnaire.objects.create(title=f"Readiness Survey {i}")

        response = self.client.get(reverse("manage_questionnaires"))
        self.assertEqual(len(response.context["page_obj"].object_list), 10)  # First page should have 10 items

        response_page_2 = self.client.get(reverse("manage_questionnaires"), {"page": 2})
        self.assertEqual(len(response_page_2.context["page_obj"].object_list), 5)  # Second page should have 5 items
