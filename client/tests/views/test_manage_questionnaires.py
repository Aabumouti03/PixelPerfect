from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from datetime import timedelta
from django.core.exceptions import ValidationError

from client.models import Questionnaire
from users.models import Questionnaire_UserResponse, EndUser

User = get_user_model()

class ManageQuestionnairesTest(TestCase):
    """Test suite for manage_questionnaires view"""

    def setUp(self):
        """Create admin and normal users, along with sample questionnaires"""
        self.client = Client()

        # Admin and normal user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.normal_user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )

        self.end_user = EndUser.objects.create(
            user=self.normal_user, age=30, gender="male", sector="it", last_time_to_work="1_month"
        )

        # Create questionnaires
        self.q1 = Questionnaire.objects.create(
            title="Workplace Confidence Survey",
            is_active=True,
            created_at=now() - timedelta(days=3)
        )
        self.q2 = Questionnaire.objects.create(
            title="Job Readiness Assessment",
            is_active=False,
            created_at=now() - timedelta(days=2)
        )
        self.q3 = Questionnaire.objects.create(
            title="Returning to Work Survey",
            is_active=False,  # not active to respect single-active rule
            created_at=now() - timedelta(days=1)
        )

        # Link responses to q1 and q2
        Questionnaire_UserResponse.objects.create(questionnaire=self.q1, user=self.end_user)
        Questionnaire_UserResponse.objects.create(questionnaire=self.q2, user=self.end_user)

    def test_redirect_if_not_logged_in(self):
        """Anonymous user should be redirected to login"""
        response = self.client.get(reverse("manage_questionnaires"))
        expected_url = reverse("log_in") + "?next=" + reverse("manage_questionnaires")
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Normal users should be redirected (not authorized)"""
        self.client.login(username="user", password="userpass")
        response = self.client.get(reverse("manage_questionnaires"))
        expected_url = reverse("log_in") + "?next=" + reverse("manage_questionnaires")
        self.assertRedirects(response, expected_url)

    def test_admin_can_access_page(self):
        """Admin can access the manage_questionnaires view"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/Manage_Questionnaires.html")

    def test_search_functionality(self):
        """Admin should see only matched questionnaires by title"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"), {"search": "Workplace"})
        self.assertContains(response, "Workplace Confidence Survey")
        self.assertNotContains(response, "Job Readiness Assessment")
        self.assertNotContains(response, "Returning to Work Survey")

    def test_filter_active_questionnaires(self):
        """Only active questionnaires should appear when filter is_active=true"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("manage_questionnaires"), {"is_active": "true"})
        self.assertContains(response, "Workplace Confidence Survey")
        self.assertNotContains(response, "Job Readiness Assessment")
        self.assertNotContains(response, "Returning to Work Survey")  

    def test_pagination(self):
        """Pagination should limit to 10 items per page"""
        self.client.login(username="admin", password="adminpass")

        # Create 12 more to trigger pagination (total 15)
        for i in range(12):
            Questionnaire.objects.create(title=f"Readiness Survey {i}")

        response = self.client.get(reverse("manage_questionnaires"))
        self.assertEqual(len(response.context["page_obj"].object_list), 10)  # Page 1

        response_page_2 = self.client.get(reverse("manage_questionnaires"), {"page": 2})
        self.assertEqual(len(response_page_2.context["page_obj"].object_list), 5)  # Page 2

    def test_only_one_active_questionnaire_allowed(self):
        """Ensure validation blocks multiple active questionnaires"""
        self.q1.is_active = True
        self.q1.save()

        # Try to create another active questionnaire
        q_new = Questionnaire(
            title="New Active One",
            is_active=True,
            created_at=now()
        )

        with self.assertRaises(ValidationError) as ctx:
            q_new.full_clean()

        self.assertIn("Only one questionnaire can be active at a time.", str(ctx.exception))
