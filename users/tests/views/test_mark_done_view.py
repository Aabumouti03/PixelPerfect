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
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username='testuser', password='testpassword')
        self.end_user = EndUser.objects.create(user=self.user)

        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        self.video_1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1")
        self.video_2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2")
        self.module.video_resources.add(self.video_1, self.video_2)

    def mark_done(self, item_id, item_type, action):
        url = reverse('mark_done')
        return self.client.post(
            url,
            json.dumps({"id": item_id, "type": item_type, "action": action}),
            content_type='application/json'
        )

    def test_mark_resource_done(self):
        response = self.mark_done(self.resource_1.id, "resource", "done")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("updated_progress", data)

        progress = UserResourceProgress.objects.get(user=self.end_user, resource=self.resource_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_resource(self):
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource_1, status="completed")
        response = self.mark_done(self.resource_1.id, "resource", "undo")
        self.assertEqual(response.status_code, 200)

        progress = UserResourceProgress.objects.get(user=self.end_user, resource=self.resource_1)
        self.assertEqual(progress.status, "not_started")

    def test_mark_exercise_done(self):
        response = self.mark_done(self.exercise_1.id, "exercise", "done")
        self.assertEqual(response.status_code, 200)

        progress = UserExerciseProgress.objects.get(user=self.end_user, exercise=self.exercise_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_exercise(self):
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise_1, status="completed")
        response = self.mark_done(self.exercise_1.id, "exercise", "undo")
        self.assertEqual(response.status_code, 200)

        progress = UserExerciseProgress.objects.get(user=self.end_user, exercise=self.exercise_1)
        self.assertEqual(progress.status, "not_started")

    def test_mark_video_done(self):
        response = self.mark_done(self.video_1.id, "video", "done")
        self.assertEqual(response.status_code, 200)

        progress = UserVideoProgress.objects.get(user=self.end_user, video=self.video_1)
        self.assertEqual(progress.status, "completed")

    def test_mark_undo_video(self):
        UserVideoProgress.objects.create(user=self.end_user, video=self.video_1, status="completed")
        response = self.mark_done(self.video_1.id, "video", "undo")
        self.assertEqual(response.status_code, 200)

        progress = UserVideoProgress.objects.get(user=self.end_user, video=self.video_1)
        self.assertEqual(progress.status, "not_started")

    def test_progress_calculation(self):
        
        total_items = 6  

        self.mark_done(self.exercise_1.id, "exercise", "done")
        self.mark_done(self.video_1.id, "video", "done")
        self.mark_done(self.resource_1.id, "resource", "done")

        user_module_progress = UserModuleProgress.objects.get(user=self.end_user, module=self.module)
        self.assertEqual(user_module_progress.completion_percentage, (3 / total_items) * 100)
