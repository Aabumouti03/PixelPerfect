from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from users.models import EndUser

User = get_user_model()

class UsersManagementViewTest(TestCase):
    def setUp(self):
        """Set up an admin user for authentication."""
        self.admin_user = User.objects.create_user(
            username="admin",
            password="adminpass",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True
        )

        self.regular_user = User.objects.create_user(
            username="user1",
            password="testpass",
            email="user1@example.com",
            is_staff=False
        )

        # Create some EndUser instances
        self.end_user1 = EndUser.objects.create(user=self.regular_user)
        self.end_user2 = EndUser.objects.create(user=User.objects.create_user(
            username="user2", password="testpass", email="user2@example.com"
        ))

    def test_users_management_view_authenticated_admin(self):
        """Test that an authenticated admin user can access the users management page."""
        self.client.login(username="admin", password="adminpass")

        response = self.client.get(reverse("users_management"))

        # Ensure response is successful
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/users_management.html")

        # Ensure users are passed to the context
        self.assertIn("users", response.context)
        self.assertEqual(response.context["users"].count(), EndUser.objects.count())

    def test_users_management_view_unauthenticated(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(reverse("users_management"))
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={reverse('users_management')}")

    def test_users_management_view_non_admin_user(self):
        """Test that a non-admin user is denied access."""
        self.client.login(username="user1", password="testpass")

        response = self.client.get(reverse("users_management"))

        # Expect a redirect (302) instead of 403
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))
