import json
from django.test import TestCase, Client
from django.urls import reverse
from django.http import JsonResponse
from client.models import Module, AdditionalResource
from django.contrib.auth import get_user_model


User = get_user_model()

class AddResourceToModuleViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        # ✅ Create a user that passes admin_check (superuser)
        self.admin_user = User.objects.create_user(
            username="AdminUser",
            password="testpass123",
            email="admin@example.com",
            is_superuser=True,  # 👈 This is what passes admin_check
        )

        # ✅ Login (username lowercased in model)
        login_success = self.client.login(username="adminuser", password="testpass123")
        self.assertTrue(login_success, "Login failed — username might not be lowercased properly!")

        self.module = Module.objects.create(title="Test Module")

        self.resource = AdditionalResource.objects.create(
            title="Test Resource",
            resource_type="book",  # Required
            status="not_started"
        )

        self.url = reverse("add_resource_to_module", args=[self.module.id])

    def test_add_resource_success(self):
        """Test successfully adding a resource to a module."""
        response = self.client.post(
            self.url,
            data=json.dumps({"resource_id": self.resource.id}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn(self.resource, self.module.additional_resources.all())

    def test_missing_resource_id(self):
        """Test missing resource_id in POST body."""
        response = self.client.post(
            self.url,
            data=json.dumps({}),  # No resource_id
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "No resource_id provided")

    def test_module_does_not_exist(self):
        """Test with a non-existent module ID."""
        invalid_url = reverse("add_resource_to_module", args=[999])  # Non-existent ID
        response = self.client.post(
            invalid_url,
            data=json.dumps({"resource_id": self.resource.id}),
            content_type="application/json"
        )
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Module not found.")

    def test_resource_does_not_exist(self):
        """Test with a non-existent resource ID."""
        response = self.client.post(
            self.url,
            data=json.dumps({"resource_id": 999}),  # Non-existent resource
            content_type="application/json"
        )
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Resource not found.")

    def test_invalid_http_method(self):
        """Test GET request returns 405 Method Not Allowed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Invalid method")

