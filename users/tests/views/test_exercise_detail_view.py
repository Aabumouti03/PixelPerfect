from django.test import TestCase
from django.urls import reverse
from users.models import User  
from users.models import EndUser
from client.models import Exercise, Section, ExerciseQuestion


class ExerciseDetailViewTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create an exercise instance and SAVE it first before adding ManyToMany fields
        self.exercise = Exercise.objects.create(title='Test Exercise', exercise_type='multiple_choice', status='not_started')

        # Create a section with a diagram
        self.section = Section.objects.create(title='Test Section', diagram='diagrams/test_diagram.png')
        self.exercise.sections.add(self.section)  # Now we can add ManyToMany fields

        # Create a test question using the correct model (ExerciseQuestion)
        self.question = ExerciseQuestion.objects.create(question_text="Sample question?", has_blank=False)
        self.exercise.questions.add(self.question)  # Add question to exercise

        # Create an EndUser instance
        self.end_user = EndUser.objects.create(user=self.user)

        # URL for the test
        self.url = reverse('exercise_detail', kwargs={'exercise_id': self.exercise.id})

    def test_exercise_detail_authenticated_user(self):
        """Test that an authenticated user can access the exercise detail page."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/exercise_detail.html')
        self.assertIn('exercise', response.context)
        self.assertEqual(response.context['exercise'], self.exercise)
        self.assertIn('diagram', response.context)
        self.assertEqual(response.context['diagram'], self.section.diagram)

    def test_exercise_detail_unauthenticated_user_redirect(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertTrue(response.url.startswith('/accounts/login/'))  # Default login URL

    def test_exercise_detail_post_request(self):
        """Test that a POST request redirects back to the same page."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, {f'answer_{self.question.id}': 'Sample answer'})

        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, self.url)