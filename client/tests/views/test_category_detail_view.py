from django.test import TestCase, Client
from django.urls import reverse
from client.models import Category, Program, Module
from users.models import User
from django.conf import settings

class CategoryDetailViewTests(TestCase):

    def setUp(self):
        """Set up test data for categories, programs, and modules."""
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

        # Create a category
        self.category = Category.objects.create(name="Test Category")

        # Create related programs and modules
        self.program1 = Program.objects.create(title="Program 1")
        self.program2 = Program.objects.create(title="Program 2")
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")

        # Assign the category to the programs and modules
        self.program1.categories.set([self.category])
        self.program2.categories.set([self.category])
        self.module1.categories.set([self.category])
        self.module2.categories.set([self.category])

        # URL for the category detail view
        self.url = reverse('category_detail', kwargs={'category_id': self.category.id})
        self.invalid_url = reverse('category_detail', kwargs={'category_id': 9999})

    def test_category_detail_requires_login(self):
        """Test that an unauthenticated user is redirected to login."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_category_detail_requires_admin(self):
        """Test that a non-admin user gets a 403 Forbidden error."""
        self.client.login(username="user1", password="userpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith(settings.LOGIN_URL))

    def test_category_detail_accessible_by_admin(self):
        """Test that an admin user can access the page."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/category_detail.html')
        self.assertIn('category', response.context)

    def test_category_detail_view_context(self):
        """Test if the correct category, programs, and modules are passed in the context."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.context['category'], self.category)
        self.assertEqual(list(response.context['programs']), [self.program1, self.program2])
        self.assertEqual(list(response.context['modules']), [self.module1, self.module2])

    def test_category_detail_view_category_not_found(self):
        """Test if the view returns 404 for a non-existing category."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view_no_programs_or_modules(self):
        """Test when the category has no programs and no modules."""
        self.client.login(username="admin", password="adminpass")
        self.category.programs.clear()
        self.category.modules.clear()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [])
        self.assertEqual(list(response.context['modules']), [])

    def test_category_detail_view_only_programs(self):
        """Test when the category has only programs, no modules."""
        self.client.login(username="admin", password="adminpass")
        self.category.modules.clear()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [self.program1, self.program2])
        self.assertEqual(list(response.context['modules']), [])

    def test_category_detail_view_only_modules(self):
        """Test when the category has only modules, no programs."""
        self.client.login(username="admin", password="adminpass")
        self.category.programs.clear()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [])
        self.assertEqual(list(response.context['modules']), [self.module1, self.module2])

    def test_category_detail_view_missing_category_id(self):
        """Test if the URL with a missing category_id raises a 404 error."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get('/category/')
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view_invalid_category_id_non_integer(self):
        """Test if passing a non-integer value raises a 404 error."""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get('/category/invalid/')
        self.assertEqual(response.status_code, 404)
