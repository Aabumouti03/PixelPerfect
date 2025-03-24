from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, ExerciseQuestion
from users.models import EndUser

User = get_user_model()

class ManageExercisesViewTest(TestCase):
    """Test suite for the manage_exercises view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create an admin user
        
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="IT")

        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="Healthcare")

        cls.question1 = ExerciseQuestion.objects.create(question_text="What is Django?")
        cls.question2 = ExerciseQuestion.objects.create(question_text="Explain Python decorators.")
        
        cls.exercise1 = Exercise.objects.create(title="Django Basics")
        cls.exercise1.questions.add(cls.question1)

        cls.exercise2 = Exercise.objects.create(title="Advanced Python")
        cls.exercise2.questions.add(cls.question2)

        cls.url = reverse('manage_exercises')

    def test_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login page"""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that non-admin users are redirected to the login page"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_user_can_access(self):
        """Test that an admin user can access the view and see exercises"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'Module/manage_exercises.html')
        
        self.assertEqual(list(response.context['exercises']), list(Exercise.objects.all()))
