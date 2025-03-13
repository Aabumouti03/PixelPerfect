from django.test import TestCase, Client
from django.urls import reverse
from users.models import EndUser, User
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.conf import settings

User = get_user_model()

class UsersManagementViewTest(TestCase):
    def setUp(self):
        """Set up test data for users."""
        self.client = Client()

        # Create admin user (superuser)
        self.admin_user = User.objects.create_user(
            username="admin",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="adminpass",
            is_superuser=True
        )

        # Create a regular (non-admin) user
        self.regular_user = User.objects.create_user(
            username="user1",
            first_name="User",
            last_name="One",
            email="user1@example.com",
            password="userpass",
            is_superuser=False
        )

        # Create an EndUser profile for the regular user
        self.enduser_profile = EndUser.objects.create(user=self.regular_user, age=25, gender="male", sector="it")

        # URL for the users management view
        self.url = reverse('users_management')

    def test_users_management_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_users_management_requires_admin(self):
        """Test that a non-admin user gets a 302 to log in page."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # Non-admin users should be forbidden

    def test_users_management_accessible_by_admin(self):
        """Test that an admin user can access the page."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)  # Admin should have access
        self.assertTemplateUsed(response, 'client/users_management.html')
        self.assertIn('users', response.context)

    def test_users_management_contains_correct_users(self):
        """Test that the view only contains EndUsers and not admins."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)

        users_list = response.context['users']
        self.assertIn(self.enduser_profile, users_list)  # Regular EndUser should be included
        self.assertNotIn(self.admin_user, users_list)  # Admin should not be in EndUsers list

    def test_users_management_with_no_users(self):
        """Test that the view handles an empty EndUser list correctly."""
        self.client.login(username="admin", password="adminpass")
        EndUser.objects.all().delete()  # Remove all EndUsers
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)
        self.assertEqual(len(response.context['users']), 0)  # No users should be found
