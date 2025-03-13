from django.test import TestCase
from django.urls import reverse
from client.models import Category
from users.models import User
from django.conf import settings

class CategoryListViewTests(TestCase):
    def setUp(self):
        """Set up test data for categories and users."""
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_superuser=True  # Ensure admin access
        )

        self.regular_user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="userpass",
            is_superuser=False
        )

        # Create different categories
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.category3 = Category.objects.create(name="Special Category @#$")
        self.category4 = Category.objects.create(name="Another category 123")
        self.category5 = Category.objects.create(name="MixedCase Category")

        self.url = reverse('category_list')  # Ensure this matches your URL pattern name

    def test_category_list_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_category_list_requires_admin(self):
        """Test that a non-admin user gets a 302 to log in page."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # Forbidden for non-admin users

    def test_category_list_accessible_by_admin(self):
        """Test that an admin user can access the page."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/category_list.html')
        self.assertIn('categories', response.context)

    def test_category_list_contains_correct_categories(self):
        """Test that the view only contains the correct categories."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)

        categories = response.context['categories']
        self.assertIn(self.category1, categories)
        self.assertIn(self.category2, categories)
        self.assertIn(self.category3, categories)
        self.assertIn(self.category4, categories)
        self.assertIn(self.category5, categories)

    def test_category_list_no_categories(self):
        """Test that the view handles an empty category list correctly."""
        self.client.login(username="admin", password="adminpass")
        Category.objects.all().delete()  # Remove all categories
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 0)

    def test_category_list_special_characters(self):
        """Test categories with special characters are correctly displayed."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        categories = response.context['categories']
        self.assertIn(self.category3, categories)  # Category with special characters should be present

