from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from client.models import Module
from client.forms import ModuleForm  # Adjust import if ModuleForm lives elsewhere

User = get_user_model()

class ClientModulesTest(TestCase):
    def setUp(self):
        """
        Creates a test user, makes them superuser, logs them in,
        and sets up sample modules and URLs.
        """
        
        self.client = Client()

        # 1. Create a normal user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        
        # 2. Make them a superuser so they pass admin_check
        self.user.is_superuser = True
        self.user.save()

        # 3. Log in as this superuser
        self.client.login(username='testuser', password='testpassword')

        # 4. Create sample modules
        self.module1 = Module.objects.create(title="Module 1", description="Description 1")
        self.module2 = Module.objects.create(title="Module 2", description="Description 2")

        # 5. Store the URLs we’ll need
        self.client_modules_url = reverse('client_modules')
        self.module_overview_url = reverse('module_overview', args=[self.module1.id])  # Not currently tested
        self.edit_module_url = reverse('edit_module', args=[self.module1.id])
        self.delete_module_url = reverse('delete_module', args=[self.module1.id])
        self.add_module_url = reverse('add_module')
        
    # 1. Test that client_modules view loads and shows modules
    def test_client_modules_view(self):
        response = self.client.get(self.client_modules_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/client_modules.html")
        self.assertContains(response, "Module 1")
        self.assertContains(response, "Module 2")

    # 2. Test color classes are assigned correctly
    def test_client_modules_color_classes(self):
        response = self.client.get(self.client_modules_url)
        modules_list = response.context['modules']
        expected_colors = ["color1", "color2", "color3", "color4", "color5", "color6"]

        for index, module in enumerate(modules_list):
            expected_color = expected_colors[index % len(expected_colors)]
            self.assertEqual(module["color_class"], expected_color)

    # 3. Test edit_module GET request (covers the 'else' branch in the view)
    def test_edit_module_get_request(self):
        response = self.client.get(self.edit_module_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/edit_module.html')

        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertIsInstance(form, ModuleForm)

        # Check if the form is pre-filled with existing data
        self.assertEqual(form.initial['title'], self.module1.title)
        self.assertEqual(form.initial['description'], self.module1.description)

    # 4. Test 404 when using an invalid module_id (currently referencing edit_module)
    def test_module_overview_404(self):
        url = reverse('edit_module', args=[9999])  # Non-existent module
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    # 5. Test adding a module (POST)
    def test_add_button_success(self):
        data = {"title": "New Module", "description": "New Description"}
        response = self.client.post(self.add_module_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Module.objects.filter(title="New Module").exists())

    # 6. Test adding a module with missing fields (stays on form)
    def test_add_button_invalid(self):
        data = {"title": "", "description": "Missing Title"}
        response = self.client.post(self.add_module_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Module.objects.filter(description="Missing Title").exists())

    # 7. Test edit_module view (POST) with valid data
    def test_edit_module_success(self):
        data = {"title": "Updated Title", "description": "Updated Description"}
        response = self.client.post(self.edit_module_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.module1.refresh_from_db()
        self.assertEqual(self.module1.title, "Updated Title")
        self.assertEqual(self.module1.description, "Updated Description")

    # 8. Test edit_module view (POST) with invalid data
    def test_edit_module_invalid_data(self):
        data = {"title": "", "description": "Updated Description"}
        response = self.client.post(self.edit_module_url, data)
        self.assertEqual(response.status_code, 200)  # Stays on form
        self.module1.refresh_from_db()
        self.assertNotEqual(self.module1.title, "")

    # 9. Test delete_module view
    def test_delete_module(self):
        response = self.client.post(self.delete_module_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Module.objects.filter(id=self.module1.id).exists())

    # 10. Test client_modules with no modules (empty state)
    def test_client_modules_empty_state(self):
        Module.objects.all().delete()
        response = self.client.get(self.client_modules_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Module 1")

    # 11. Test authentication required
    def test_authentication_required(self):
        self.client.logout()
        response = self.client.get(self.client_modules_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/log_in/', response.url)