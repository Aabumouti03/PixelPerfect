from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, UserModuleProgress, UserExerciseProgress, UserResourceProgress, UserVideoProgress
from client.models import Module, Exercise, AdditionalResource, Section, VideoResource

User = get_user_model()

class ModuleOverviewViewTest(TestCase):

    def setUp(self):
        """Set up test user, module, exercises, resources, and videos."""
        # ✅ Create a test user and log them in
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.end_user = EndUser.objects.create(user=self.user)

        # ✅ Create a module
        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        # ✅ Create a section and add exercises
        self.section = Section.objects.create(title="Section 1", description="Section Description")

        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice")

        self.section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(self.section)

        # ✅ Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf")

        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # ✅ Create video resources
        self.video_1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1")
        self.video_2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2")

        self.module.video_resources.add(self.video_1, self.video_2)  # ✅ Correctly link videos to module

        # ✅ Track user-specific progress
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise_1, status="completed")
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource_1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video_1, status="completed")


    def test_module_overview_view(self):
        """Test if module overview page loads correctly with expected context."""
        url = reverse('module_overview', kwargs={'module_id': self.module.id})
        response = self.client.get(url)

        # ✅ Check response status
        self.assertEqual(response.status_code, 200)

        # ✅ Ensure the correct template is used
        self.assertTemplateUsed(response, 'users/moduleOverview.html')

        # ✅ Check context data
        self.assertIn('module', response.context)
        self.assertEqual(response.context['module'], self.module)

        self.assertIn('exercises', response.context)
        self.assertEqual(len(response.context['exercises']), 2)  # Expecting 2 exercises

        self.assertIn('additional_resources', response.context)
        self.assertEqual(len(response.context['additional_resources']), 2)  # Expecting 2 resources

        self.assertIn('video_resources', response.context)
        self.assertEqual(len(response.context['video_resources']), 2)  # Expecting 2 videos

        self.assertIn('user_exercise_progress', response.context)
        self.assertEqual(response.context['user_exercise_progress'][self.exercise_1.id], "completed")

        self.assertIn('user_resource_progress', response.context)
        self.assertEqual(response.context['user_resource_progress'][self.resource_1.id], "completed")

        self.assertIn('user_video_progress', response.context)
        self.assertEqual(response.context['user_video_progress'][self.video_1.id], "completed")


    def test_progress_calculation(self):
        """Test that the progress calculation works correctly for a specific user."""
        # ✅ Calculate expected progress
        total_items = 2 + 2 + 2  # 2 exercises + 2 resources + 2 videos
        completed_items = 1 + 1 + 1  # 1 completed exercise + 1 completed resource + 1 completed video
        expected_progress_value = (completed_items / total_items) * 100  # Should be 50%

        # ✅ Fetch the view response
        url = reverse('module_overview', kwargs={'module_id': self.module.id})
        response = self.client.get(url)

        # ✅ Ensure progress calculation is correct
        self.assertEqual(response.context['progress_value'], expected_progress_value)
