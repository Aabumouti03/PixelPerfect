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

    def test_trigger_form_error(self):
        """Ensure duplicate titles (case-insensitive) are rejected and form.add_error is triggered."""
        self.client.login(username='adminuser', password='password123')

        # Create a program first to trigger duplicate error
        Program.objects.create(title="Duplicate Program", description="Existing program")

        duplicate_data = {"title": "Duplicate Program", "description": "Attempt duplicate creation"}

        response = self.client.post(self.create_program_url, duplicate_data)

        # Ensure the page reloads instead of redirecting
        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        # Explicitly check if "title" has an error due to form.add_error()
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(form.errors["title"], ["A program with this title already exists."])

        # Ensure only one instance of the program exists
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

    def test_post_create_program_with_existing_new_category(self):
        """Ensure a new category is not duplicated if it already exists."""
        self.client.login(username='adminuser', password='password123')

        existing_category = Category.objects.create(name="Existing Category")

        valid_data = self.valid_program_data.copy()
        valid_data["new_category"] = "Existing Category"

        response = self.client.post(self.create_program_url, valid_data, follow=True)

        self.assertRedirects(response, self.programs_url)

        program = Program.objects.get(title="Test Program")
        self.assertIn(existing_category, program.categories.all())  # Should reuse the existing category
        self.assertEqual(Category.objects.filter(name="Existing Category").count(), 1)  # No duplicates


    def test_post_create_program_with_whitespace_new_category(self):
        """Ensure new_category containing only whitespace is ignored."""
        self.client.login(username='adminuser', password='password123')

        valid_data = self.valid_program_data.copy()
        valid_data["new_category"] = "   "  # Only whitespace

        response = self.client.post(self.create_program_url, valid_data, follow=True)

        self.assertRedirects(response, self.programs_url)

        program = Program.objects.get(title="Test Program")

        self.assertEqual(program.categories.count(), 0)  # No new category should be added
        self.assertFalse(Category.objects.filter(name="   ").exists())  # No whitespace category created

    def test_post_create_program_with_selected_categories(self):
        """Ensure selected categories are assigned to the program."""
        self.client.login(username='adminuser', password='password123')

        valid_data = self.valid_program_data.copy()
        valid_data["categories"] = [self.category.id]  # Select existing category

        response = self.client.post(self.create_program_url, valid_data, follow=True)

        self.assertRedirects(response, self.programs_url)

        program = Program.objects.get(title="Test Program")
        self.assertIn(self.category, program.categories.all())  # Category should be assigned

    def test_create_program_redirects_unauthenticated_users(self):
        """Ensure unauthenticated users are redirected to login when accessing create_program."""
        response = self.client.get(self.create_program_url)

        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(response.url.startswith(reverse("log_in")))  # Should redirect to login

    def test_create_program_denies_access_to_regular_users(self):
        """Ensure regular (non-admin) users cannot access the create program page."""
        self.client.login(username='regularuser', password='password123')

        response = self.client.get(self.create_program_url)

        self.assertNotEqual(response.status_code, 200)  # Should return a forbidden or redirect response

    def test_post_create_program_invalid_form_no_description(self):
        """Ensure form submission fails if description is missing but title is unique."""
        self.client.login(username='adminuser', password='password123')

        invalid_data = {
            "title": "Valid Unique Title",
            "description": "",  # Missing description
            "module_order": f"{self.module1.id}",
        }

        response = self.client.post(self.create_program_url, invalid_data)

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertFalse(form.is_valid())

        # Make sure "title" does NOT have an error (because it's not a duplicate)
        self.assertNotIn("title", form.errors)

        # Ensure "description" field has an error
        self.assertIn("description", form.errors)

        # Ensure the program was NOT created
        self.assertFalse(Program.objects.filter(title="Valid Unique Title").exists())

    def test_create_program_denied_for_non_admin(self):
        """Ensure a non-admin user is redirected when trying to access create_program."""
        self.client.login(username="regularuser", password="password123")

        response = self.client.get(self.create_program_url, follow=True)

        # Check that the user is redirected to login
        expected_redirect_url = reverse("log_in") + f"?next={self.create_program_url}"
        self.assertRedirects(response, expected_redirect_url)

    def test_post_create_program_with_new_category(self):
        """Ensure a new category is created and linked to the program."""
        self.client.login(username='adminuser', password='password123')

        valid_data = self.valid_program_data.copy()
        valid_data["new_category"] = "New Category"

        response = self.client.post(self.create_program_url, valid_data, follow=True)

        self.assertRedirects(response, self.programs_url)

        # Ensure program is created
        self.assertTrue(Program.objects.filter(title="Test Program").exists())
        program = Program.objects.get(title="Test Program")

        # Ensure new category exists
        self.assertTrue(Category.objects.filter(name="New Category").exists())
        new_category = Category.objects.get(name="New Category")

        # Ensure the new category is associated with the program
        self.assertIn(new_category, program.categories.all())

    def test_post_create_program_without_login(self):
        """Ensure that an unauthenticated user cannot create a program."""
        response = self.client.post(self.create_program_url, self.valid_program_data, follow=True)

        # Ensure user is redirected to login page
        expected_redirect = reverse("log_in") + f"?next={self.create_program_url}"
        self.assertRedirects(response, expected_redirect)

        # Ensure the program was not created
        self.assertFalse(Program.objects.filter(title="Test Program").exists())


    def test_get_create_program_page_as_admin(self):
        """Ensure the create program page loads correctly for an admin user."""
        self.client.login(username='adminuser', password='password123')

        response = self.client.get(self.create_program_url)

        # Ensure correct response and template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")

        # Ensure form is included in context
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ProgramForm)

        # Ensure categories exist in the context
        self.assertIn("categories", response.context)
        self.assertEqual(list(response.context["categories"]), list(Category.objects.all()))

    def test_post_create_program_invalid_form(self):
        """Ensure an invalid form submission doesn't create a program and returns errors."""
        self.client.login(username='adminuser', password='password123')

        invalid_data = {"title": "", "description": ""}  # Missing required fields
        response = self.client.post(self.create_program_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertFalse(Program.objects.exists())
        self.assertIn("title", response.context["form"].errors)
        self.assertIn("description", response.context["form"].errors)

    def test_create_program_redirects_non_admins(self):
        """Ensure non-admin users are redirected when trying to access create_program."""
        self.client.login(username="regularuser", password="password123")
        response = self.client.get(self.create_program_url, follow=True)

        expected_redirect_url = reverse("log_in") + f"?next={self.create_program_url}"
        self.assertRedirects(response, expected_redirect_url)

    def test_create_program_redirects_anonymous_users(self):
        """Ensure unauthenticated users are redirected to login when accessing create_program."""
        response = self.client.get(self.create_program_url)

        expected_redirect_url = reverse("log_in") + f"?next={self.create_program_url}"
        self.assertRedirects(response, expected_redirect_url)

    def test_post_create_program_invalid_title(self):
        """Ensure program creation fails if the title is empty or just whitespace."""
        self.client.login(username='adminuser', password='password123')
        
        invalid_data = {"title": "  ", "description": "Invalid title"}
        response = self.client.post(self.create_program_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertFalse(Program.objects.exists())

    def test_create_program_template_rendering(self):
        """Ensure the create program page renders with the expected context."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(self.create_program_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], ProgramForm)
        self.assertIn("categories", response.context)
        self.assertEqual(list(response.context["categories"]), list(Category.objects.all()))
