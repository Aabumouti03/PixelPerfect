from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import VideoResource
from users.models import User  

class DeleteVideoTestCase(TestCase):

    def setUp(self):
        """Create a user, video resource, and log in."""
        self.user = User.objects.create_user(username="testuser", password="testpassword", email="testuser@example.com")
        self.video = VideoResource.objects.create(title="Test Video", youtube_url="http://example.com/video")
        
        self.client.login(username="testuser", password="testpassword")

    def test_delete_video_success(self):
        """Test that a video is deleted and the user is redirected to the video list page."""
        video_id = self.video.id
        url = reverse("delete_video", args=[video_id])

        self.assertEqual(VideoResource.objects.count(), 1)

        self.video.delete()

        self.assertEqual(VideoResource.objects.count(), 0)

        response = self.client.get(reverse("video_list"))

        self.assertEqual(response.status_code, 302) 
    
class DeleteVideoAsAdminTestCase(TestCase):

    def setUp(self):
        """Create an admin user, video resource, and log in."""
        self.admin_user = User.objects.create_user(
            username="adminuser",
            password="adminpassword",
            email="adminuser@example.com"
        )
        self.admin_user.is_staff = True 
        self.admin_user.save()

        self.video = VideoResource.objects.create(
            title="Test Video",
            youtube_url="http://example.com/video"
        )
        
        self.client.login(username="adminuser", password="adminpassword")

    def test_delete_video_success_admin(self):

        """Test that an admin user can delete a video and is redirected to the video list page."""
        video_id = self.video.id
        url = reverse("delete_video", args=[video_id])

        self.assertEqual(VideoResource.objects.count(), 1)

        self.video.delete()

        self.assertEqual(VideoResource.objects.count(), 0)

        response = self.client.get(reverse("video_list"))

        self.assertEqual(response.status_code, 302) 
        
class DeleteVideoNoPermissionTestCase(TestCase):
    
    def setUp(self):
        """Create a non-admin user, video resource, and log in."""
        self.non_admin_user = User.objects.create_user(
            username="nonadminuser",
            password="nonadminpassword",
            email="nonadminuser@example.com"
        )
        self.video = VideoResource.objects.create(
            title="Test Video",
            youtube_url="http://example.com/video"
        )
        
        self.client.login(username="nonadminuser", password="nonadminpassword")

    def test_delete_video_no_permission(self):
        """Test that a non-admin user cannot delete a video and is redirected to the login page."""
        video_id = self.video.id
        url = reverse("delete_video", args=[video_id])

        response = self.client.post(url)

        self.assertEqual(VideoResource.objects.count(), 1)

        self.assertRedirects(response, reverse('log_in') + '?next=' + url)

       




    

    
