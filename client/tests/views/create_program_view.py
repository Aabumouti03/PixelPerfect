from django.test import TestCase
from django.urls import reverse
from client.models import Program, Module, ProgramModule
from client.forms import ProgramForm

class CreateProgramViewTests(TestCase):

    def setUp(self):
        """Set up test data."""
        self.create_program_url = reverse("programs")  # Ensure this URL is correctly mapped
        self.module1 = Module.objects.create(title="Module 1", description="Test module 1")
        self.module2 = Module.objects.create(title="Module 2", description="Test module 2")

    def test_render_create_program_form(self):
        """Test that the view renders the create program form on GET request."""
        response = self.client.get(self.create_program_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertIsInstance(response.context["form"], ProgramForm)

    def test_create_program_successfully(self):
        """Test that a program is created and modules are assigned in order."""
        data = {
            "title": "Test Program",
            "description": "A sample test program",
            "module_order": f"{self.module1.id},{self.module2.id}"
        }

        response = self.client.post(self.create_program_url, data)

        self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertRedirects(response, self.create_program_url)

        # Ensure the program is created
        program = Program.objects.get(title="Test Program")
        self.assertEqual(program.description, "A sample test program")

        # Check module order
        modules = ProgramModule.objects.filter(program=program).order_by("order")
        self.assertEqual(modules.count(), 2)
        self.assertEqual(modules[0].module, self.module1)
        self.assertEqual(modules[1].module, self.module2)

    def test_create_program_with_invalid_module(self):
        """Test that the view handles invalid module IDs gracefully."""
        data = {
            "title": "Program with Invalid Module",
            "description": "Test with one invalid module",
            "module_order": f"{self.module1.id},999"  # 999 is an invalid module ID
        }

        response = self.client.post(self.create_program_url, data)

        self.assertEqual(response.status_code, 302)  # Should still redirect
        self.assertRedirects(response, self.create_program_url)

        # Ensure the program is created but only with valid modules
        program = Program.objects.get(title="Program with Invalid Module")
        modules = ProgramModule.objects.filter(program=program)
        self.assertEqual(modules.count(), 1)
        self.assertEqual(modules[0].module, self.module1)  # Only valid module should be added

    def test_create_program_invalid_form(self):
        """Test that an invalid form does not create a program."""
        data = {
            "title": "",  # Title is required, so this is invalid
            "description": "This should not be saved"
        }

        response = self.client.post(self.create_program_url, data)

        # The page should re-render with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_program.html")
        self.assertContains(response, "This field is required.")  # Ensure validation message is shown
        self.assertFalse(Program.objects.filter(description="This should not be saved").exists())

