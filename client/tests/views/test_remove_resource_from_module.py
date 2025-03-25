from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, AdditionalResource
from users.models import EndUser
import json

User = get_user_model()

class RemoveResourceFromModuleTest(TestCase):
    """Test suite for the remove_resource_from_module view."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=30, gender='male', sector='IT')

        cls.module = Module.objects.create(title="Sample Module", description="Module description")

        cls.resource1 = AdditionalResource.objects.create(title="Resource 1", file="path/to/resource1.pdf")
        cls.resource2 = AdditionalResource.objects.create(title="Resource 2", file="path/to/resource2.pdf")
        
        cls.module.additional_resources.add(cls.resource1, cls.resource2)
        
        cls.url = reverse('remove_resource_from_module', args=[cls.module.id])

    def test_admin_can_remove_resource(self):
        """Test successful removal of a resource by an admin."""
        self.client.login(username='adminuser', password='adminpass')
        
        data = json.dumps({"resource_ids": [self.resource1.id]})
        response = self.client.post(self.url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        self.module.refresh_from_db()
        self.assertNotIn(self.resource1, self.module.additional_resources.all())

    def test_invalid_resource_id(self):
        """Test trying to remove a resource that doesn't exist."""
        self.client.login(username='adminuser', password='adminpass')
        
        data = json.dumps({"resource_ids": [9999]})
        response = self.client.post(self.url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "success": False,
            "error": "AdditionalResource matching query does not exist."
        })

    def test_non_admin_user_cannot_remove_resource(self):
        """Test that a non-admin user is denied access."""
        normal_user = User.objects.create_user(username='normaluser', password='userpass')
        EndUser.objects.create(user=normal_user, age=25, gender='female', sector='Health')

        self.client.login(username='normaluser', password='userpass')
        
        data = json.dumps({"resource_ids": [self.resource2.id]})
        response = self.client.post(self.url, data, content_type='application/json')
        
        expected_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, expected_url)
        
        self.module.refresh_from_db()
        self.assertIn(self.resource2, self.module.additional_resources.all())
    
    def test_no_resource_id_provided(self):
        """Test if the request body doesn't contain resource_ids."""
        self.client.login(username="adminuser", password="adminpass")
        response = self.client.post(
            self.url,
            json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            "success": False,
            "error": "No resource_ids provided"
        })

    def test_get_request_instead_of_post(self):
        """Test if a GET request is sent instead of a POST request."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid method"})
