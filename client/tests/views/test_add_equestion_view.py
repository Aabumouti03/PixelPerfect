from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import ExerciseQuestion
from users.models import EndUser
from client.forms import ExerciseQuestionForm

User = get_user_model()


class AddEQuestionViewTest(TestCase):
    """Test suite for the add_Equestion view."""

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

        # URL for the view
        cls.url = reverse('add_question')

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a non-admin user is denied access."""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)
        

    def test_admin_user_can_access(self):
        """Test that an admin user can access the view."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_question.html')
        self.assertIsInstance(response.context['form'], ExerciseQuestionForm)

    def test_successful_question_creation(self):
        """Test successful creation of a question by an admin."""
        self.client.login(username='adminuser', password='adminpass')
        
        # Submit valid data to the form
        response = self.client.post(self.url, {
            'question_text': 'What is Django?',
            'has_blank': False
        })
        
        # Check if the question was saved
        self.assertEqual(ExerciseQuestion.objects.count(), 1)
        self.assertRedirects(response, reverse('add_exercise'))

    def test_invalid_form_submission(self):
        """Test submission of an invalid form."""
        self.client.login(username='adminuser', password='adminpass')
        
        # Submit form without a question_text
        response = self.client.post(self.url, {
            'question_text': '',  # Missing question text
            'has_blank': False
        })
        
        # Check if the page is re-rendered with the form errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_question.html')
        
        # Verify the form is bound and contains errors
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('question_text', form.errors)
        self.assertEqual(form.errors['question_text'], ['This field is required.'])
