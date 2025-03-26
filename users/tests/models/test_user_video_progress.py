from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserVideoProgress
from client.models import VideoResource

User = get_user_model()

class UserVideoProgressTest(TestCase):
    def test_video_progress(self):
        user = User.objects.create_user(username='videouser', password='pass')
        end_user = EndUser.objects.create(user=user)
        video = VideoResource.objects.create(title="Video Title", description="Video desc")

        progress = UserVideoProgress.objects.create(user=end_user, video=video, status='in_progress')
        self.assertEqual(str(progress), "videouser - Video Title: in_progress")