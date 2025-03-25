from django.test import TestCase
from django.contrib.auth import get_user_model
from client.models import Questionnaire, ExerciseQuestion  # We keep these imports if these models exist
from users.models import (
    Admin,
    EndUser,
    UserProgramEnrollment,
    UserModuleEnrollment,
    UserProgramProgress,
    UserModuleProgress,
    UserResourceProgress,
    UserExerciseProgress,
    UserVideoProgress,
    UserResponse,
    Questionnaire_UserResponse,
)
from client.models import Program, Module, Exercise, AdditionalResource, VideoResource

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        """
        Ensure we can create a User and that the __str__ or full_name behaves as expected.
        """
        user = User.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.full_name(), 'John Doe')

    def test_user_str_method(self):
        user = User.objects.create_user(username='jane', password='pass', first_name='Jane', last_name='Doe')
        # Typically, AbstractUser's __str__ is the username
        self.assertEqual(str(user), 'jane')
        

class EndUserModelTest(TestCase):
    def test_create_end_user(self):
        """
        Ensure we can create an EndUser with a linked User.
        """
        user = User.objects.create_user(username='enduser', password='pass', first_name='End', last_name='User')
        end_user = EndUser.objects.create(
            user=user,
            age=25,
            gender='male',
            last_time_to_work='1_month',
            sector='it',
        )
        self.assertEqual(str(end_user), 'User: End User')  # checks __str__ method
        self.assertEqual(end_user.age, 25)
        self.assertEqual(end_user.gender, 'male')

class UserProgramEnrollmentTest(TestCase):
    def test_create_enrollment(self):
        """
        Ensure we can enroll a user in a program and check __str__.
        """
        user = User.objects.create_user(username='proguser', password='pass')
        end_user = EndUser.objects.create(user=user, age=20)
        program = Program.objects.create(title='Test Program', description='Description')

        enrollment = UserProgramEnrollment.objects.create(user=end_user, program=program)
        self.assertIn(enrollment, program.enrolled_users.all())  # program.enrolled_users returns UserProgramEnrollment
        self.assertEqual(str(enrollment), f"{end_user.user.username} enrolled in {program.title}")
        

class UserModuleEnrollmentTest(TestCase):
    def test_create_module_enrollment(self):
        user = User.objects.create_user(username='moduser', password='pass')
        end_user = EndUser.objects.create(user=user, age=22)
        module = Module.objects.create(title="Test Module", description="Desc")

        enrollment = UserModuleEnrollment.objects.create(user=end_user, module=module)
        self.assertIn(enrollment, module.enrolled_users.all())
        self.assertEqual(str(enrollment), "moduser started Test Module")
        

class UserModuleProgressTest(TestCase):
    def test_module_progress(self):
        user = User.objects.create_user(
            username='progressuser',
            password='pass',
            first_name='Progress',
            last_name='User'
        )
        end_user = EndUser.objects.create(user=user)
        module = Module.objects.create(title="Progress Module", description="Desc")

        progress = UserModuleProgress.objects.create(user=end_user, module=module, completion_percentage=50.0)
        self.assertEqual(progress.status, 'not_started')

        self.assertEqual(str(progress), "Progress User - Progress Module (not_started)")

        with self.assertRaises(Exception):
            UserModuleProgress.objects.create(user=end_user, module=module)
            

class UserResourceProgressTest(TestCase):
    def test_resource_progress(self):
        user = User.objects.create_user(username='resourceuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        resource = AdditionalResource.objects.create(
            resource_type='book',
            title="Extra Resource",
            description="Resource content"
        )

        progress = UserResourceProgress.objects.create(user=end_user, resource=resource, status='in_progress')
        self.assertEqual(str(progress), "resourceuser - Extra Resource: in_progress")

        # Test unique_together
        with self.assertRaises(Exception):
            UserResourceProgress.objects.create(user=end_user, resource=resource)
            

class UserExerciseProgressTest(TestCase):
    def test_exercise_progress(self):
        user = User.objects.create_user(username='exerciseuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        exercise = Exercise.objects.create(title="Test Exercise")

        progress = UserExerciseProgress.objects.create(user=end_user, exercise=exercise, status='completed')
        self.assertEqual(str(progress), "exerciseuser - Test Exercise: completed")
        

class UserVideoProgressTest(TestCase):
    def test_video_progress(self):
        user = User.objects.create_user(username='videouser', password='pass')
        end_user = EndUser.objects.create(user=user)
        video = VideoResource.objects.create(title="Video Title", description="Video desc")

        progress = UserVideoProgress.objects.create(user=end_user, video=video, status='in_progress')
        self.assertEqual(str(progress), "videouser - Video Title: in_progress")
        

class UserResponseTest(TestCase):
    def test_create_user_response(self):
        user = User.objects.create_user(username='resuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        exercise_question = ExerciseQuestion.objects.create(question_text="Sample Q")

        user_response = UserResponse.objects.create(
            user=end_user,
            question=exercise_question,
            response_text="User's answer"
        )
        self.assertEqual(str(user_response), f"Response by resuser for {exercise_question}")
        

class QuestionnaireUserResponseTest(TestCase):
    def test_questionnaire_user_response(self):
        user = User.objects.create_user(username='questuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        questionnaire = Questionnaire.objects.create(title="Q1", description="...")

        q_user_response = Questionnaire_UserResponse.objects.create(user=end_user, questionnaire=questionnaire)
        self.assertIsNotNone(q_user_response.started_at)
        self.assertIsNone(q_user_response.completed_at)
        
class UserGravatarTest(TestCase):
    def test_gravatar(self):
        user = User.objects.create_user(username='gravuser', password='pass', email='test@example.com')
        url = user.gravatar(size=200)
        self.assertIn('size=200', url)
        self.assertIn('www.gravatar.com', url)

    def test_mini_gravatar(self):
        user = User.objects.create_user(username='minigrav', password='pass', email='mini@example.com')
        url = user.mini_gravatar()
        # By default, it calls gravatar(size=60)
        self.assertIn('size=60', url)
        self.assertIn('www.gravatar.com', url)
        
class AdminModelTest(TestCase):
    def test_admin_str(self):
        user = User.objects.create_user(
            username='adminUser',
            password='pass',
            first_name='Admin',
            last_name='Test'
        )
        admin_profile = Admin.objects.create(user=user)
        self.assertEqual(str(admin_profile), "Admin: Admin Test")
        
class UserProgramProgressTest(TestCase):
    def test_user_program_progress_str(self):
        user = User.objects.create_user(username='testprog', password='pass', first_name='Prog', last_name='User')
        end_user = EndUser.objects.create(user=user)
        program = Program.objects.create(title='My Program')
        progress = UserProgramProgress.objects.create(user=end_user, program=program, status='in_progress')
        
        self.assertEqual(str(progress), "Prog User - My Program (in_progress)")