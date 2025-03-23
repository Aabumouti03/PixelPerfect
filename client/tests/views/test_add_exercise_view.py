from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import ExerciseQuestion, Exercise
from client.forms import ExerciseForm
from users.models import EndUser

User = get_user_model()

class AddExerciseViewTest(TestCase):
    """Test suite for the add_exercise view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create an admin user and associated profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # Create a normal user and associated profile
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # Create some questions
        cls.question1 = ExerciseQuestion.objects.create(question_text="What is Django?")
        cls.question2 = ExerciseQuestion.objects.create(question_text="Explain MVC pattern.")
        
        # URL for the view
        cls.url = reverse('add_exercise')

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page"""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a non-admin user is denied access"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_user_can_access(self):
        """Test that an admin user can access the view"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_exercise.html')
        self.assertIsInstance(response.context['form'], ExerciseForm)
        
        # ✅ Check if all questions are available in the context
        questions_in_context = response.context['questions']
        self.assertIn(self.question1, questions_in_context)
        self.assertIn(self.question2, questions_in_context)

    def test_successful_exercise_creation(self):
        """Test successful creation of a new exercise by an admin"""
        self.client.login(username='adminuser', password='adminpass')
        
        # Form data to be posted
        response = self.client.post(self.url, {
            'title': 'New Exercise',
            'exercise_type': 'short_answer',
            'questions': [self.question1.id, self.question2.id]
        })
        
        # ✅ Check redirection to 'add_section'
        self.assertRedirects(response, reverse('add_section'))
        
        # Check if the exercise was successfully created
        self.assertTrue(Exercise.objects.filter(title='New Exercise').exists())
        new_exercise = Exercise.objects.get(title='New Exercise')
        
        # ✅ Verify the exercise type and associated questions
        self.assertEqual(new_exercise.exercise_type, 'short_answer')
        self.assertIn(self.question1, new_exercise.questions.all())
        self.assertIn(self.question2, new_exercise.questions.all())

    def test_invalid_form_submission(self):
        """Test that an invalid form submission re-renders the form with errors"""
        self.client.login(username='adminuser', password='adminpass')
        
        # Submit an invalid form (empty title)
        response = self.client.post(self.url, {
            'title': '',  # Missing title, which is required
            'exercise_type': 'short_answer'
        })
        
        # Check if the response is a successful page load (re-rendered form)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_exercise.html')
        
        # Check if form errors are displayed properly
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('title', form.errors)
        self.assertEqual(form.errors['title'], ['This field is required.'])


