from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Program, ProgramModule, Module, Category
from client.forms import ProgramForm

class CreateProgramViewTestCase(TestCase):
    """Tests for the create_program view."""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='password123'
        )
        self.regular_user = User.objects.create_user(
            username='regularuser', email='regular@example.com', password='password123'
        )

        self.category = Category.objects.create(name="Technology")
        
        self.module1 = Module.objects.create(title="Module 1", description="First module")
        self.module2 = Module.objects.create(title="Module 2", description="Second module")

        self.create_program_url = reverse("create_program")
        self.programs_url = reverse("programs")

        self.valid_program_data = {
            "title": "Test Program",
            "description": "A test program",
            "module_order": f"{self.module1.id},{self.module2.id}",
        }

    def test_get_create_program_page_as_admin(self):
        """Ensure the create program page loads correctly for an admin user."""
        self.client.login(username='adminuser', password='password123')
        
        response = self.client.get(self.create_program_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertIsInstance(response.context["form"], ProgramForm)

    def test_get_create_program_page_as_regular_user(self):
        """Ensure a regular user cannot access the create program page."""
        self.client.login(username='regularuser', password='password123')
        
        response = self.client.get(self.create_program_url)
        
        self.assertNotEqual(response.status_code, 200)

    def test_post_valid_create_program(self):
        """Ensure a valid program submission creates a program and assigns modules."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.post(self.create_program_url, self.valid_program_data, follow=True)
        
        self.assertRedirects(response, self.programs_url)
        self.assertTrue(Program.objects.filter(title="Test Program").exists())

    def test_post_create_program_missing_modules(self):
        """Ensure the program is created even if some modules are missing."""
        self.client.login(username='adminuser', password='password123')
        missing_module_data = {
            "title": "Program With Missing Module",
            "description": "A test program",
            "module_order": f"{self.module1.id},999",
        }
        response = self.client.post(self.create_program_url, missing_module_data, follow=True)
        
        self.assertRedirects(response, self.programs_url)
        
        program = Program.objects.get(title="Program With Missing Module")
        
        self.assertEqual(program.program_modules.count(), 1)

    def test_post_create_program_no_modules(self):
        """Ensure a program is created even when no modules are selected."""
        self.client.login(username='adminuser', password='password123')
        no_module_data = {
            "title": "No Modules Program",
            "description": "This program has no modules.",
            "module_order": "",
        }
        response = self.client.post(self.create_program_url, no_module_data, follow=True)
        self.assertRedirects(response, self.programs_url)
        
        program = Program.objects.get(title="No Modules Program")
        
        self.assertEqual(program.program_modules.count(), 0)

    def test_post_create_program_duplicate_title(self):
        """Ensure duplicate titles (case-insensitive) are rejected."""
        self.client.login(username='adminuser', password='password123')
        Program.objects.create(title="Duplicate Program", description="Existing program")
        duplicate_data = {"title": "duplicate program", "description": "Attempt duplicate creation"}
        response = self.client.post(self.create_program_url, duplicate_data)
        
        self.assertEqual(response.status_code, 200)
        
        form = response.context["form"]
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(Program.objects.filter(title__iexact="Duplicate Program").count(), 1)

    def test_post_create_program_invalid_module_ids(self):
        """Ensure invalid module IDs in module_order are safely ignored."""
        self.client.login(username='adminuser', password='password123')
        data_with_invalid_ids = {
            "title": "Program with Invalid Module IDs",
            "description": "Test invalid IDs",
            "module_order": f"{self.module1.id},abc,-1,;",
        }
        response = self.client.post(self.create_program_url, data_with_invalid_ids, follow=True)
        
        self.assertRedirects(response, self.programs_url)
        
        program = Program.objects.get(title="Program with Invalid Module IDs")
        self.assertEqual(program.program_modules.count(), 1)

    def test_post_create_program_with_whitespace_title(self):
        """Ensure program creation fails if the title is just whitespace."""
        self.client.login(username='adminuser', password='password123')
        whitespace_title_data = {"title": "    ", "description": "Invalid title"}
        response = self.client.post(self.create_program_url, whitespace_title_data)
        self.assertEqual(response.status_code, 200)
        
        form = response.context["form"]
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertFalse(Program.objects.exists())

    def test_post_create_program_without_login(self):
        """Ensure that an unauthenticated user cannot create a program."""
        response = self.client.post(self.create_program_url, self.valid_program_data)
        
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Program.objects.filter(title="Test Program").exists())
    
    def test_get_create_program_page_as_admin(self):
        """Ensure the create program page loads correctly for an admin user."""
        self.client.login(username='adminuser', password='password123')
        
        response = self.client.get(self.create_program_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertIsInstance(response.context["form"], ProgramForm)
        self.assertIn("categories", response.context)

    def test_post_create_program_with_invalid_data(self):
        """Ensure invalid form submissions are handled properly."""
        self.client.login(username='adminuser', password='password123')
        invalid_data = {"title": "", "description": ""}
        
        response = self.client.post(self.create_program_url, invalid_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertFalse(Program.objects.exists())

    def test_post_create_program_preserves_module_order(self):
        """Ensure that module order is correctly preserved."""
        self.client.login(username='adminuser', password='password123')
        ordered_data = {
            "title": "Ordered Modules Program",
            "description": "Check module ordering",
            "module_order": f"{self.module2.id},{self.module1.id}",
        }
        response = self.client.post(self.create_program_url, ordered_data, follow=True)
        self.assertRedirects(response, self.programs_url)
        program = Program.objects.get(title="Ordered Modules Program")
        module_ids = list(program.program_modules.order_by('order').values_list('module_id', flat=True))
        self.assertEqual(module_ids, [self.module2.id, self.module1.id])


    def test_post_create_program_without_login(self):
        """Ensure that an unauthenticated user cannot create a program."""
        response = self.client.post(self.create_program_url, self.valid_program_data)
        
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(Program.objects.filter(title="Test Program").exists())

    def test_post_create_program_existing_title_fails(self):
        """Ensure that trying to create a program with an existing title fails and does not update."""
        self.client.login(username='adminuser', password='password123')

       
        Program.objects.create(title="Existing Program", description="Original description")

        
        duplicate_data = {
            "title": "Existing Program",  # Duplicate title
            "description": "Updated description",
            "module_order": f"{self.module2.id}",
        }

        response = self.client.post(self.create_program_url, duplicate_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        form = response.context["form"]
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

        
        program = Program.objects.get(title="Existing Program")
        self.assertEqual(program.description, "Original description")

    def test_post_create_program_duplicate_title_with_whitespace(self):
        """Ensure duplicate titles with extra whitespace are rejected."""
        self.client.login(username='adminuser', password='password123')

        
        Program.objects.create(title="Whitespace Duplicate", description="Original")

        duplicate_data = {
            "title": "   Whitespace Duplicate   ",  # extra spaces
            "description": "Should be rejected",
        }

        response = self.client.post(self.create_program_url, duplicate_data)
        self.assertEqual(response.status_code, 200)
        
        form = response.context["form"]
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(Program.objects.filter(title__iexact="Whitespace Duplicate").count(), 1)
