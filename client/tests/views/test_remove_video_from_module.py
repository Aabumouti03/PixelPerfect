from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, VideoResource
from users.models import EndUser
import json

User = get_user_model()

class RemoveVideoFromModuleViewTest(TestCase):
    """Test suite for the remove_video_from_module view."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")

        # Create a module and a video
        cls.module = Module.objects.create(title="Test Module", description="A sample module description")
        cls.video = VideoResource.objects.create(
            title="Test Video",
            description="A test video description",
            youtube_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )

        # Associate the video with the module
        cls.module.video_resources.add(cls.video)

        # Define the URL for the view
        cls.url = reverse('remove_video_from_module', args=[cls.module.id])

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page."""
        response = self.client.post(self.url, json.dumps({'video_ids': [self.video.id]}), content_type="application/json")
        expected_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, expected_url)

    def test_non_admin_user_cannot_remove_resource(self):
        """Test if a non-admin user is redirected to login."""
        self.client.login(username='normaluser', password='userpass')
        
        response = self.client.post(self.url, json.dumps({'video_ids': [self.video.id]}), content_type="application/json")
        
        expected_url = reverse('log_in') + f"?next={self.url}"
        self.assertRedirects(response, expected_url)

    
    def test_successful_video_removal(self):
        """Test successful removal of a video from a module by an admin."""
        self.client.login(username='adminuser', password='adminpass')
        
        # Ensure the video is linked to the module
        self.assertIn(self.video, self.module.video_resources.all())
        
        response = self.client.post(self.url, json.dumps({'video_ids': [self.video.id]}), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        self.module.refresh_from_db()
        self.assertNotIn(self.video, self.module.video_resources.all())

    def test_video_does_not_exist(self):
        """Test trying to remove a non-existent video."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({'video_ids': [9999]}), content_type="application/json")
        
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {"success": False, "error": "Video with ID 9999 does not exist."})

    def test_invalid_request_method(self):
        """Test handling of non-POST requests."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid method"})
    
    def test_missing_video_ids(self):
        """Test if no video IDs are provided in the request body."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({}), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "No video IDs provided"})
    
    def test_invalid_json_format(self):
        """Test if invalid JSON format is provided."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, data="Invalid JSON", content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid JSON format"})
