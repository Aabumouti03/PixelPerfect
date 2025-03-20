from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import (
    EndUser, UserModuleProgress, UserProgramProgress, 
    UserExerciseProgress, UserResourceProgress, UserVideoProgress
)
from client.models import Module, Exercise, AdditionalResource, Program, ProgramModule, Section, VideoResource
from users.helpers_modules import calculate_progress, calculate_program_progress, update_user_program_progress

User = get_user_model() 

class ProgressCalculationTests(TestCase):

    def setUp(self):
        """Set up test data for progress calculations."""

        # ✅ Create a test user before creating EndUser
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # ✅ Create test EndUser linked to a real user
        self.end_user = EndUser.objects.create(user=self.user)

        # ✅ Create a test program
        self.program = Program.objects.create(title="Test Program", description="Sample Program")

        # ✅ Create test modules
        self.module1 = Module.objects.create(title="Module 1", description="Description")
        self.module2 = Module.objects.create(title="Module 2", description="Description")

        # ✅ Create a ProgramModule intermediary to link program & modules
        ProgramModule.objects.create(program=self.program, module=self.module1, order=1)
        ProgramModule.objects.create(program=self.program, module=self.module2, order=2)

        # ✅ Create sections
        self.section1 = Section.objects.create(title="Section 1")
        self.section2 = Section.objects.create(title="Section 2")

        # ✅ Link sections to modules
        self.module1.sections.add(self.section1)
        self.module2.sections.add(self.section2)

        # ✅ Create exercises, additional resources, and videos
        self.exercise1 = Exercise.objects.create(title="Exercise 1", exercise_type="short_answer")
        self.exercise2 = Exercise.objects.create(title="Exercise 2", exercise_type="short_answer")

        self.resource1 = AdditionalResource.objects.create(title="Resource 1", resource_type="pdf")
        self.resource2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf")

        self.video1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1")
        self.video2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2")

        # ✅ Link exercises to sections
        self.section1.exercises.add(self.exercise1)
        self.section2.exercises.add(self.exercise2)

        # ✅ Link resources to modules
        self.module1.additional_resources.add(self.resource1)
        self.module2.additional_resources.add(self.resource2)

        # ✅ Link videos to modules
        self.module1.video_resources.add(self.video1)
        self.module2.video_resources.add(self.video2)

    def test_calculate_progress_with_all_completed(self):
        """Test progress calculation when all exercises, resources, and videos are completed."""

        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise1, status="completed")
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise2, status="completed")

        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource1, status="completed")
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource2, status="completed")

        UserVideoProgress.objects.create(user=self.end_user, video=self.video1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video2, status="completed")

        progress = calculate_progress(self.end_user, self.module1)
        self.assertEqual(progress, 100)

    def test_calculate_progress_with_no_completions(self):
        """Test progress calculation when no exercises, resources, or videos are completed."""
        progress = calculate_progress(self.end_user, self.module1)
        self.assertEqual(progress, 0)

    def test_calculate_progress_with_partial_completions(self):
        """Test progress calculation when some exercises, resources, or videos are completed."""
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video1, status="completed")

        progress = calculate_progress(self.end_user, self.module1)
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)

    def test_calculate_program_progress_no_completed_modules(self):
        """Test program progress calculation when no modules are completed."""
        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 0)

    def test_calculate_program_progress_with_one_completed_module(self):
        """Test program progress calculation when one module is completed."""
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)

        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 50)

    def test_calculate_program_progress_with_all_completed_modules(self):
        """Test program progress calculation when all modules are completed."""
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        UserModuleProgress.objects.create(user=self.end_user, module=self.module2, completion_percentage=100)

        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 100)

    def test_update_user_program_progress(self):
        """Test updating a user's program progress in the database."""
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        update_user_program_progress(self.end_user, self.program)

        user_program_progress = UserProgramProgress.objects.get(user=self.end_user, program=self.program)
        self.assertEqual(user_program_progress.completion_percentage, 50)
