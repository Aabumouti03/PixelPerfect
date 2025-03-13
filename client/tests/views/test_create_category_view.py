from django.test import TestCase, Client
from django.urls import reverse
from client.models import Category, Module, Program
from client.forms import CategoryForm
from users.models import User
from django.conf import settings

class CreateCategoryViewTests(TestCase):

    def setUp(self):
        """Set up test data for modules, programs, and users."""
        self.client = Client()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_superuser=True  # Ensures admin access
        )

        # Create a regular (non-admin) user
        self.regular_user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="userpass",
            is_superuser=False
        )

        # Create some modules and programs
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.program1 = Program.objects.create(title="Program 1")
        self.program2 = Program.objects.create(title="Program 2")

        # URL for the category creation view
        self.url = reverse('create_category')

    def test_create_category_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_create_category_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # Non-admin users should be forbidden

    def test_create_category_get_as_admin(self):
        """Test that an admin user can access the category creation form."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/create_category.html')
        self.assertIsInstance(response.context['form'], CategoryForm)

    def test_create_category_post_valid(self):
        """Test POST with valid data."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': 'New Category',
            'modules': [self.module1.id, self.module2.id],
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created
        category = Category.objects.get(name='New Category')
        self.assertEqual(category.modules.count(), 2)
        self.assertEqual(category.programs.count(), 2)

    def test_create_category_post_no_modules_or_programs(self):
        """Test POST with no modules or programs selected."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': 'New Category No Modules or Programs',
            'modules': [],
            'programs': [],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created without any modules or programs
        category = Category.objects.get(name='New Category No Modules or Programs')
        self.assertEqual(category.modules.count(), 0)
        self.assertEqual(category.programs.count(), 0)

    def test_create_category_post_invalid(self):
        """Test POST with invalid data (e.g., missing required fields)."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': '',  # Invalid because 'name' is required
            'modules': [],
            'programs': [],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed
        self.assertTrue(response.context['form'].errors)  # Check for errors

    def test_create_category_post_no_data(self):
        """Test POST with no data submitted."""
        self.client.login(username="admin", password="adminpass")
        data = {}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_create_category_post_invalid_modules_ids(self):
        """Test POST with invalid module IDs."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': 'Invalid Category',
            'modules': [999],  # Non-existent module ID
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_create_category_post_invalid_programs_ids(self):
        """Test POST with invalid program IDs."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': 'Invalid Programs Category',
            'modules': [self.module1.id, self.module2.id],
            'programs': [999],  # Non-existent program ID
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_create_category_post_blank_name(self):
        """Test POST with a blank name."""
        self.client.login(username="admin", password="adminpass")
        data = {
            'name': '',
            'modules': [self.module1.id, self.module2.id],
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_create_category_post_non_admin(self):
        """Test that a non-admin user cannot create a category."""
        self.client.login(username="user1", password="userpass")
        data = {
            'name': 'Unauthorized Category',
            'modules': [self.module1.id],
            'programs': [self.program1.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))  # Non-admin users should be forbidden
        self.assertFalse(Category.objects.filter(name="Unauthorized Category").exists())  # Ensure category was not created
