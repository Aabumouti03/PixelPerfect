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
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.end_user = EndUser.objects.create(user=self.user)

        self.program = Program.objects.create(title="Test Program", description="Sample Program")

        self.module1 = Module.objects.create(title="Module 1", description="Description")
        self.module2 = Module.objects.create(title="Module 2", description="Description")

        ProgramModule.objects.create(program=self.program, module=self.module1, order=1)
        ProgramModule.objects.create(program=self.program, module=self.module2, order=2)

        self.section1 = Section.objects.create(title="Section 1")
        self.section2 = Section.objects.create(title="Section 2")

        self.module1.sections.add(self.section1)
        self.module2.sections.add(self.section2)

        self.exercise1 = Exercise.objects.create(title="Exercise 1", exercise_type="short_answer")
        self.exercise2 = Exercise.objects.create(title="Exercise 2", exercise_type="short_answer")

        self.resource1 = AdditionalResource.objects.create(title="Resource 1", resource_type="pdf")
        self.resource2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf")

        self.video1 = VideoResource.objects.create(title="Video 1", youtube_url="https://youtu.be/video1")
        self.video2 = VideoResource.objects.create(title="Video 2", youtube_url="https://youtu.be/video2")

        self.section1.exercises.add(self.exercise1)
        self.section2.exercises.add(self.exercise2)

        self.module1.additional_resources.add(self.resource1)
        self.module2.additional_resources.add(self.resource2)

        self.module1.video_resources.add(self.video1)
        self.module2.video_resources.add(self.video2)

    def test_calculate_progress_with_all_completed(self):
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise1, status="completed")
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise2, status="completed")
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource1, status="completed")
        UserResourceProgress.objects.create(user=self.end_user, resource=self.resource2, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video2, status="completed")

        progress = calculate_progress(self.end_user, self.module1)
        self.assertEqual(progress, 100)

    def test_calculate_progress_with_no_completions(self):
        progress = calculate_progress(self.end_user, self.module1)
        self.assertEqual(progress, 0)

    def test_calculate_progress_with_partial_completions(self):
        UserExerciseProgress.objects.create(user=self.end_user, exercise=self.exercise1, status="completed")
        UserVideoProgress.objects.create(user=self.end_user, video=self.video1, status="completed")

        progress = calculate_progress(self.end_user, self.module1)
        self.assertGreater(progress, 0)
        self.assertLess(progress, 100)

    def test_calculate_program_progress_no_completed_modules(self):
        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 0)

    def test_calculate_program_progress_with_one_completed_module(self):
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 50)

    def test_calculate_program_progress_with_all_completed_modules(self):
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        UserModuleProgress.objects.create(user=self.end_user, module=self.module2, completion_percentage=100)
        progress = calculate_program_progress(self.end_user, self.program)
        self.assertEqual(progress, 100)

    def test_update_user_program_progress(self):
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        update_user_program_progress(self.end_user, self.program)
        user_program_progress = UserProgramProgress.objects.get(user=self.end_user, program=self.program)
        self.assertEqual(user_program_progress.completion_percentage, 50)

    def test_calculate_program_progress_with_no_modules(self):
        empty_program = Program.objects.create(title="Empty Program", description="No modules")
        progress = calculate_program_progress(self.end_user, empty_program)
        self.assertEqual(progress, 0)
