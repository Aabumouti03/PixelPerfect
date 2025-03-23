from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from client.models import VideoResource

class VideoResourceModelTest(TestCase):
    def test_get_embed_url_standard(self):
        video = VideoResource.objects.create(
            title="Test Video",
            youtube_url="https://www.youtube.com/watch?v=abc123"
        )
        expected_embed = "https://www.youtube.com/embed/abc123"
        self.assertEqual(video.get_embed_url(), expected_embed)

    def test_get_embed_url_shortened(self):
        video = VideoResource.objects.create(
            title="Short Video",
            youtube_url="https://youtu.be/xyz789"
        )
        expected_embed = "https://www.youtube.com/embed/xyz789"
        self.assertEqual(video.get_embed_url(), expected_embed)

    def test_get_embed_url_invalid(self):
        video = VideoResource.objects.create(
            title="Invalid Video",
            youtube_url="https://www.example.com/watch?v=invalid"
        )
        self.assertIsNone(video.get_embed_url())

    def test_str(self):
        video = VideoResource.objects.create(
            title="Test Video 2",
            youtube_url="https://youtu.be/def456"
        )
        self.assertEqual(str(video), "Test Video 2")

    def test_get_embed_url_with_extra_parameters(self):
        """Test that extra query parameters do not affect embed URL extraction."""
        video = VideoResource.objects.create(
            title="Extra Params Video",
            youtube_url="https://www.youtube.com/watch?v=abc123&feature=share"
        )
        expected_embed = "https://www.youtube.com/embed/abc123"
        self.assertEqual(video.get_embed_url(), expected_embed)

    def test_default_status(self):
        """Test that the default status is 'not_started'."""
        video = VideoResource.objects.create(
            title="Default Status Video",
            youtube_url="https://youtu.be/ghi789"
        )
        self.assertEqual(video.status, "not_started")

    def test_set_status_valid(self):
        """Test that setting a valid status works correctly."""
        video = VideoResource.objects.create(
            title="Completed Video",
            youtube_url="https://youtu.be/jkl012",
            status="completed"
        )
        self.assertEqual(video.status, "completed")

    def test_description_optional(self):
        """Test that the description field is optional and defaults to None."""
        video = VideoResource.objects.create(
            title="No Description Video",
            youtube_url="https://youtu.be/mno345"
        )
        self.assertIsNone(video.description)

    def test_set_description(self):
        """Test that setting a description works as expected."""
        desc = "A sample description for the video resource."
        video = VideoResource.objects.create(
            title="Description Video",
            youtube_url="https://youtu.be/pqr678",
            description=desc
        )
        self.assertEqual(video.description, desc)

    def test_update_video_resource(self):
        """Test that a VideoResource can be updated and saved correctly."""
        video = VideoResource.objects.create(
            title="Initial Title",
            youtube_url="https://youtu.be/stu901",
            description="Initial description.",
            status="not_started"
        )
        # Update fields
        video.title = "Updated Title"
        video.youtube_url = "https://www.youtube.com/watch?v=updated123"
        video.description = "Updated description."
        video.status = "completed"
        video.save()
        video.refresh_from_db()
        self.assertEqual(video.title, "Updated Title")
        self.assertEqual(video.get_embed_url(), "https://www.youtube.com/embed/updated123")
        self.assertEqual(video.description, "Updated description.")
        self.assertEqual(video.status, "completed")

    def test_get_embed_url_empty_youtu_be(self):
        """Test that a shortened URL without a video ID returns None."""
        video = VideoResource.objects.create(
            title="Empty Youtu.be",
            youtube_url="https://youtu.be/"
        )
        self.assertIsNone(video.get_embed_url())

    def test_get_embed_url_no_v_parameter(self):
        """Test that a YouTube URL missing the 'v' parameter returns None."""
        video = VideoResource.objects.create(
            title="No V Param Video",
            youtube_url="https://www.youtube.com/watch?feature=share"
        )
        self.assertIsNone(video.get_embed_url())

    def test_youtube_url_with_trailing_slash(self):
        """Test that a shortened URL with a trailing slash is handled correctly."""
        video = VideoResource.objects.create(
            title="Trailing Slash Video",
            youtube_url="https://youtu.be/abc123/"
        )
        expected_embed = "https://www.youtube.com/embed/abc123/"
        self.assertEqual(video.get_embed_url(), expected_embed)

    def test_invalid_youtube_url_scheme(self):
        """Test that a URL with an unsupported scheme returns a valid embed URL given current implementation."""
        video = VideoResource.objects.create(
            title="Invalid Scheme Video",
            youtube_url="ftp://youtu.be/abc123"
        )
        expected_embed = "https://www.youtube.com/embed/abc123"
        self.assertEqual(video.get_embed_url(), expected_embed)

    def test_whitespace_in_youtube_url(self):
        """Test that leading/trailing whitespace in the URL is preserved in the embed URL given current implementation."""
        video = VideoResource.objects.create(
            title="Whitespace URL Video",
            youtube_url="   https://youtu.be/abc123   "
        )
        expected_embed = "https://www.youtube.com/embed/abc123   "
        self.assertEqual(video.get_embed_url(), expected_embed)

