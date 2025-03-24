from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import VideoResource, Module
from users.models import EndUser
from django.contrib.messages import get_messages

User = get_user_model()

class AddVideoViewTest(TestCase):
    """Test suite for the add_video view."""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create an admin user and associated profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="IT")
        
        # Create a normal user and associated profile
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.normal_profile = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # Create a module for linking purposes
        cls.module = Module.objects.create(title='Test Module')
        
        # URL for the add_video view
        cls.url = reverse('add_video')

    def test_admin_can_add_video(self):
        """Test that an admin user can successfully add a video."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, {
            'title': 'Test Video',
            'description': 'This is a test video',
            'youtube_url': 'https://www.youtube.com/watch?v=example'
        })

        self.assertEqual(VideoResource.objects.count(), 1)
        self.assertRedirects(response, '/')
        
        # Check if the success message was sent
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Video added successfully." in str(m) for m in messages))

    def test_admin_can_add_video_and_link_to_module(self):
        """Test that a video can be added and linked to a module if module_id is provided."""
        self.client.login(username='adminuser', password='adminpass')
        
        url_with_module = f"{self.url}?module_id={self.module.id}"
        
        response = self.client.post(url_with_module, {
            'title': 'Linked Video',
            'description': 'This video is linked to a module',
            'youtube_url': 'https://www.youtube.com/watch?v=linked_example'
        })

        self.assertEqual(VideoResource.objects.count(), 1)
        video = VideoResource.objects.get(title='Linked Video')
        self.assertIn(video, self.module.video_resources.all())
        self.assertRedirects(response, '/')
        
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Video added and linked to module." in str(m) for m in messages))

    def test_access_denied_for_non_admin(self):
        """Test that a normal user cannot access the add video page."""
        self.client.login(username='normaluser', password='userpass')
        
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_invalid_form_submission(self):
        """Test that an invalid form submission re-renders the form with errors."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, {
            'description': 'This video has no title or URL'  # Missing required fields: title, youtube_url
        })
        
        # Confirm the form didn't save any VideoResource
        self.assertEqual(VideoResource.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        # Check if the form has errors
        form = response.context.get('form')
        self.assertIn('title', form.errors)
        self.assertIn('youtube_url', form.errors)


    def test_get_request_renders_form(self):
        """Test that a GET request renders the video form correctly."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/add_video.html')
