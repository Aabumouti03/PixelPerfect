from django.test import TestCase
from django.urls import reverse
from users.models import User
from client.models import Exercise, AdditionalResource, Module, Section, VideoResource
from users.models import EndUser, UserModuleProgress
import json


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
        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank", status="in_progress")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice", status="in_progress")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        # ✅ Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book", status="in_progress")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf", status="in_progress")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # ✅ Create video resources
        self.video_1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1", status="in_progress")
        self.video_2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2", status="in_progress")
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
        self.resource_1.refresh_from_db()
        self.assertEqual(self.resource_1.status, "completed")


    def test_mark_undo_resource(self):
        """Test undoing a completed additional resource."""
        self.resource_1.status = "completed"
        self.resource_1.save()

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.resource_1.id,
            "type": "resource",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.resource_1.refresh_from_db()
        self.assertEqual(self.resource_1.status, "in_progress")


    def test_mark_exercise_done(self):
        """Test marking an exercise as completed."""
        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "done"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.exercise_1.refresh_from_db()
        self.assertEqual(self.exercise_1.status, "completed")


    def test_mark_undo_exercise(self):
        """Test undoing a completed exercise."""
        self.exercise_1.status = "completed"
        self.exercise_1.save()

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.exercise_1.refresh_from_db()
        self.assertEqual(self.exercise_1.status, "in_progress")


    def test_mark_video_done(self):
        """Test marking a video as completed."""
        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.video_1.id,
            "type": "video",
            "action": "done"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.video_1.refresh_from_db()
        self.assertEqual(self.video_1.status, "completed")


    def test_mark_undo_video(self):
        """Test undoing a completed video."""
        self.video_1.status = "completed"
        self.video_1.save()

        url = reverse('mark_done')
        response = self.client.post(url, json.dumps({
            "id": self.video_1.id,
            "type": "video",
            "action": "undo"
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.video_1.refresh_from_db()
        self.assertEqual(self.video_1.status, "in_progress")


    def test_progress_calculation(self):
        """Test that progress updates correctly when items are completed."""
        exercises = [self.exercise_1, self.exercise_2]
        additional_resources = [self.resource_1, self.resource_2]
        videos = [self.video_1, self.video_2]

        total_items = len(exercises) + len(additional_resources) + len(videos)
        completed_items = 0  # Initially, all items are "in_progress"

        expected_progress_value = (completed_items / total_items) * 100

        self.assertEqual(expected_progress_value, 0)

        # ✅ Mark one exercise and one video as done
        self.exercise_1.status = "completed"
        self.video_1.status = "completed"
        self.exercise_1.save()
        self.video_1.save()

        # ✅ Recalculate progress
        completed_items = 2  # 1 completed exercise + 1 completed video
        expected_progress_value = (completed_items / total_items) * 100

        # ✅ Ensure it updates correctly
        self.assertEqual(expected_progress_value, (2 / 6) * 100)
