from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db.models.query import QuerySet
from client.models import VideoResource
from unittest.mock import patch

User = get_user_model()

@patch("client.views.admin_check", lambda u: True)
class VideoListViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",  
            password="regularpass",
            is_staff=False
        )
        self.url = reverse("video_list")

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_non_admin_user_redirected(self):
        self.client.login(username="regular", password="regularpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_admin_user_access(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "client/video_list.html")

    def test_context_contains_videos(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertIn("videos", response.context)

    def test_context_videos_is_queryset(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["videos"], QuerySet)

    def test_no_videos(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(self.url)
        self.assertEqual(response.context["videos"].count(), 0)

    def test_one_video_in_context(self):
        self.client.login(username="admin", password="adminpass")
        VideoResource.objects.create(
            title="Video 1", youtube_url="https://www.youtube.com/watch?v=abc123"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context["videos"].count(), 1)

    def test_multiple_videos_in_context(self):
        self.client.login(username="admin", password="adminpass")
        VideoResource.objects.create(
            title="Video 1", youtube_url="https://youtu.be/abc123"
        )
        VideoResource.objects.create(
            title="Video 2", youtube_url="https://youtu.be/def456"
        )
        response = self.client.get(self.url)
        self.assertEqual(response.context["videos"].count(), 2)

    def test_view_allows_post(self):
        self.client.login(username="admin", password="adminpass")
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_reverse_url_resolution(self):
        url = reverse("video_list")
        self.assertTrue(url)

    def test_video_queryset_is_all_videos(self):
        self.client.login(username="admin", password="adminpass")
        VideoResource.objects.create(
            title="Video 1", youtube_url="https://youtu.be/abc123"
        )
        VideoResource.objects.create(
            title="Video 2", youtube_url="https://youtu.be/def456"
        )
        response = self.client.get(self.url)
        qs = VideoResource.objects.all()
        self.assertQuerySetEqual(
            response.context["videos"],
            [repr(x) for x in qs],
            ordered=False,
            transform=repr
        )


    def test_non_admin_user_redirects_with_next(self):
        response = self.client.get(self.url)
        self.assertIn("next=", response.url)

    def test_admin_access_after_logout_fails(self):
        self.client.login(username="admin", password="adminpass")
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_view_renders_correct_content(self):
        self.client.login(username="admin", password="adminpass")
        VideoResource.objects.create(
            title="Test Video", youtube_url="https://youtu.be/test"
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test Video")
