from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import VideoResource
from users.models import EndUser

User = get_user_model()

class VideoDetailViewTest(TestCase):
    """Test suite for the video_detail view."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        # Create a regular user
        cls.regular_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.regular_user, age=30, gender="female", sector="healthcare")

        # Create a sample video
        cls.video = VideoResource.objects.create(
            title='Test Video',
            description='A sample video description',
            youtube_url='https://www.youtube.com/watch?v=sample'
        )

        # URL for the video detail view
        cls.url = reverse('video_detail', args=[cls.video.id])

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, expected_url)

    def test_redirect_if_not_admin(self):
        """Test if a non-admin user is redirected to the login page."""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + f'?next={self.url}'
        self.assertRedirects(response, expected_url)

    def test_admin_can_access_video_detail(self):
        """Test if an admin user can successfully access the video detail view."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        # ✅ Check for successful access
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/video_detail.html')
        self.assertContains(response, 'Test Video')
        self.assertContains(response, 'A sample video description')

    def test_non_existent_video(self):
        """Test accessing a non-existent video returns a 404 error."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('video_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)
