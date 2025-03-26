from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire
from users.models import EndUser, Questionnaire_UserResponse

User = get_user_model()


class ViewRespondersTest(TestCase):
    """Test suite for view_responders view"""

    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass",
            first_name="Admin", last_name="User"
        )

        # Create normal user 1
        self.normal_user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="userpass",
            first_name="John", last_name="Doe"
        )
        self.end_user1 = EndUser.objects.create(user=self.normal_user1, age=30, gender="female", sector="healthcare")

        # Create normal user 2
        self.normal_user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="userpass",
            first_name="Jane", last_name="Smith"
        )
        self.end_user2 = EndUser.objects.create(user=self.normal_user2, age=25, gender="male", sector="finance")

        # Create a questionnaire
        self.questionnaire = Questionnaire.objects.create(
            title="Workplace Readiness Survey",
            description="Assessing readiness to return to work",
            is_active=True
        )

        # Associate responses with users
        self.response1 = Questionnaire_UserResponse.objects.create(
            questionnaire=self.questionnaire, user=self.end_user1
        )
        self.response2 = Questionnaire_UserResponse.objects.create(
            questionnaire=self.questionnaire, user=self.end_user2
        )

    def test_redirect_if_not_logged_in(self):
        """Test that non-authenticated users are redirected"""
        response = self.client.get(reverse("view_responders", args=[self.questionnaire.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("view_responders", args=[self.questionnaire.id])
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a normal user is redirected and cannot view responders"""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(reverse("view_responders", args=[self.questionnaire.id]))
        expected_url = reverse("log_in") + "?next=" + reverse("view_responders", args=[self.questionnaire.id])
        self.assertRedirects(response, expected_url)

    def test_admin_can_view_responders(self):
        """Test that an admin can view responders"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("view_responders", args=[self.questionnaire.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/view_responders.html")
        self.assertContains(response, self.end_user1.user.first_name)
        self.assertContains(response, self.end_user2.user.first_name)

    def test_search_responders(self):
        """Test that search filters responders correctly"""
        self.client.login(username="admin", password="adminpass")

        # Search by first name of EndUser1
        search_term = self.end_user1.user.first_name  

        response = self.client.get(reverse("view_responders", args=[self.questionnaire.id]), {"search": search_term})

        # Ensure EndUser1 appears in search results
        self.assertContains(response, self.end_user1.user.first_name)

        # Ensure EndUser2 does NOT appear in search results
        self.assertNotContains(response, self.end_user2.user.first_name)

    def test_pagination(self):
        """Test that pagination works"""
        self.client.login(username="admin", password="adminpass")

        # Create 12 more responders (total = 14)
        for i in range(12):
            new_user = User.objects.create_user(username=f"user{i+3}", email=f"user{i+3}@example.com", password="userpass")
            new_end_user = EndUser.objects.create(user=new_user, age=28, gender="female", sector="education")
            Questionnaire_UserResponse.objects.create(questionnaire=self.questionnaire, user=new_end_user)

        response = self.client.get(reverse("view_responders", args=[self.questionnaire.id]))
        self.assertEqual(len(response.context["page_obj"].object_list), 10)  # First page should have 10 items

        response_page_2 = self.client.get(reverse("view_responders", args=[self.questionnaire.id]), {"page": 2})
        self.assertEqual(len(response_page_2.context["page_obj"].object_list), 4)  # Second page should have 4 items
