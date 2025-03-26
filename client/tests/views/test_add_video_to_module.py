from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, VideoResource
import json

User = get_user_model()

class AddVideoToModuleViewTest(TestCase):
    def setUp(self):
     self.client = Client()
     self.admin_user = User.objects.create_superuser(
        username='admin', email='admin@test.com', password='adminpass'
    )
     self.regular_user = User.objects.create_user(
        username='user', email='user@test.com', password='userpass'
    )

     self.module = Module.objects.create(title="Test Module", description="Some description")
     self.video = VideoResource.objects.create(
        title="Test Video",
        youtube_url="https://youtu.be/dQw4w9WgXcQ"
    )

     self.url = reverse('add_video_to_module', args=[self.module.id])


    def test_admin_can_add_video_to_module(self):
        self.client.login(username='admin', password='adminpass')
        payload = {"video_id": self.video.id}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Video added to module."})
        self.assertIn(self.video, self.module.video_resources.all())

    def test_video_id_missing(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.url, data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "No video_id provided"})

    def test_module_not_found(self):
        self.client.login(username='admin', password='adminpass')
        bad_url = reverse('add_video_to_module', args=[9999])
        response = self.client.post(bad_url, data=json.dumps({"video_id": self.video.id}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "error": "Module not found."})

    def test_video_not_found(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(self.url, data=json.dumps({"video_id": 9999}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "error": "Video not found."})

    def test_invalid_method(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid method"})

    def test_reject_unauthenticated_user(self):
        payload = {"video_id": self.video.id}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("log_in"), response.url)

    def test_reject_non_admin_user(self):
        self.client.login(username='user', password='userpass')
        payload = {"video_id": self.video.id}
        response = self.client.post(self.url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("log_in"), response.url)
