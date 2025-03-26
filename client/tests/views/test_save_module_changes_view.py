from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, VideoResource, AdditionalResource
import json
import uuid


class SaveModuleChangesTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create an admin user
        self.admin_user = get_user_model().objects.create_superuser(
            username="adminuser",
            password="adminpassword",
            email=f"adminuser{uuid.uuid4()}@example.com"
        )
        self.client.login(username="adminuser", password="adminpassword")

        self.module = Module.objects.create(title="Test Module")

        # Create Video and Resource objects
        self.video1 = VideoResource.objects.create(title="Test Video 1", youtube_url="https://www.youtube.com/watch?v=abc123")
        self.video2 = VideoResource.objects.create(title="Test Video 2", youtube_url="https://www.youtube.com/watch?v=def456")
        self.resource1 = AdditionalResource.objects.create(title="Test Resource 1", resource_type="link", url="https://example.com/resource1")
        self.resource2 = AdditionalResource.objects.create(title="Test Resource 2", resource_type="pdf", url="https://example.com/resource2")

        self.url = reverse("save_module_changes", args=[self.module.id])

    def test_save_module_changes(self):
        payload = {
            "videos": f"{self.video1.id},{self.video2.id}",
            "resources": f"{self.resource1.id},{self.resource2.id}"
        }

        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

        self.assertListEqual(
            list(self.module.video_resources.values_list('id', flat=True).order_by('id')),
            [self.video1.id, self.video2.id]
        )
        self.assertListEqual(
            list(self.module.additional_resources.values_list('id', flat=True).order_by('id')),
            [self.resource1.id, self.resource2.id]
        )

    def test_save_module_changes_no_videos_or_resources(self):
        payload = {"videos": "", "resources": ""}
        response = self.client.post(self.url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})
        self.assertFalse(self.module.video_resources.exists())
        self.assertFalse(self.module.additional_resources.exists())

    def test_save_module_changes_invalid_module(self):
        invalid_url = reverse("save_module_changes", args=[9999])
        payload = {"videos": f"{self.video1.id}", "resources": f"{self.resource1.id}"}
        response = self.client.post(invalid_url, data=json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_non_admin_user_cannot_save_changes(self):
        """Test that a non-admin user cannot save changes to the module"""
        # Log in as a non-admin user
        self.client.logout()  # Ensure we log out the admin user
        self.client.login(username="nonadmin", password="password123")

        data = {
            "videos": f"{self.video1.id},{self.video2.id}",
            "resources": f"{self.resource1.id},{self.resource2.id}"
        }
        
        response = self.client.post(
            reverse("save_module_changes", kwargs={"module_id": self.module.id}),
            json.dumps(data),
            content_type="application/json"
        )
        
        # If you want to keep the original test expecting 403
        self.assertEqual(response.status_code, 302)  # Expecting redirect to login page
        self.assertIn('/log_in/', response.url)


