from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, UserModuleProgress, UserExerciseProgress, UserResourceProgress, UserVideoProgress
from client.models import Module, Exercise, AdditionalResource, Section, VideoResource
import json
from users.helpers_modules import calculate_progress

User = get_user_model()


class MarkDoneViewTest(TestCase):

    def setUp(self):
        """Set up test user, module, exercises, resources, and videos."""
        # ✅ Create a test user and log them in
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username='testuser', password='testpassword')

        # ✅ Create an EndUser profile for the user
        self.end_user = EndUser.objects.create(user=self.user)

        # ✅ Create a Module
        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        # ✅ Create exercises and add them to a Section
        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        # ✅ Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # ✅ Create video resources
        self.video_1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1")
        self.video_2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2")
        self.module.video_resources.add(self.video_1, self.video_2)

    def test_mark_resource_done(self):
        """Test marking an additional resource as completed."""
        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.resource_1.id,
            "type": "resource",
            "action": "done"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        # ✅ Check UserResourceProgress table for the user
        progress = UserResourceProgress.objects.get(user=self.end_user, resource=self.resource_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_resource(self):
        """Test undoing a completed additional resource."""
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource_1, status="completed")

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.resource_1.id,
            "type": "resource",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        progress = UserResourceProgress.objects.get(user=self.end_user, resource=self.resource_1)
        self.assertEqual(progress.status, "not_started")

    def test_mark_exercise_done(self):
        """Test marking an exercise as completed."""
        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "done"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        progress = UserExerciseProgress.objects.get(user=self.end_user, exercise=self.exercise_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_exercise(self):
        """Test undoing a completed exercise."""
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise_1, status="completed")

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        progress = UserExerciseProgress.objects.get(user=self.end_user, exercise=self.exercise_1)
        self.assertEqual(progress.status, "not_started")

    def test_mark_video_done(self):
        """Test marking a video as completed."""
        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.video_1.id,
            "type": "video",
            "action": "done"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        progress = UserVideoProgress.objects.get(user=self.end_user, video=self.video_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_video(self):
        """Test undoing a completed video."""
        UserVideoProgress.objects.create(user=self.end_user, video=self.video_1, status="completed")

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.video_1.id,
            "type": "video",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)

        progress = UserVideoProgress.objects.get(user=self.end_user, video=self.video_1)
        self.assertEqual(progress.status, "not_started")

    def test_progress_calculation(self):
        """Test that progress updates correctly when items are completed."""
        total_items = 2 + 2 + 2  # 2 exercises + 2 resources + 2 videos
        completed_items = 0  # Initially, all items are "not_started"

        expected_progress_value = (completed_items / total_items) * 100
        self.assertEqual(expected_progress_value, 0)

        # ✅ Mark one exercise and one video as done
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise_1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video_1, status="completed")

        # ✅ Fix: Use `get_or_create()` to prevent `DoesNotExist` error
        user_module_progress, created = UserModuleProgress.objects.get_or_create(user=self.end_user, module=self.module)
        user_module_progress.completion_percentage = calculate_progress(self.end_user, self.module)
        user_module_progress.save()

        # ✅ Recalculate progress
        completed_items = 2  # 1 completed exercise + 1 completed video
        expected_progress_value = (completed_items / total_items) * 100

        # ✅ Ensure progress is updated correctly
        self.assertEqual(user_module_progress.completion_percentage, expected_progress_value)
