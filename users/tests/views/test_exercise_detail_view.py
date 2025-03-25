from django.test import TestCase
from django.urls import reverse
from users.models import User, EndUser, UserResponse
from client.models import Exercise, ExerciseQuestion


class ExerciseDetailViewViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.exercise = Exercise.objects.create(title='Test Exercise View', exercise_type='multiple_choice', status='not_started')

        self.question = ExerciseQuestion.objects.create(question_text="What is Django?", has_blank=False)
        self.exercise.questions.add(self.question)

        self.end_user = EndUser.objects.create(user=self.user)

        self.user_response = UserResponse.objects.create(
            user=self.end_user,
            question=self.question,
            response_text="Django is a web framework.",
            submitted_at="2025-03-25 10:00:00"
        )

        self.url = reverse('exercise_detail_view', kwargs={'exercise_id': self.exercise.id})


    def test_exercise_detail_view_authenticated_user(self):
        """Test that an authenticated user can access the exercise detail view and see their responses."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserResponce/exercise_detail.html')
        self.assertIn('exercise', response.context)
        self.assertEqual(response.context['exercise'], self.exercise)
        self.assertIn('questions_with_responses', response.context)
        
        questions_with_responses = response.context['questions_with_responses']
        self.assertEqual(len(questions_with_responses), 1)
        
        question_data = questions_with_responses[0]
        self.assertEqual(question_data['question'], self.question)
        self.assertEqual(len(question_data['responses']), 1)
        self.assertEqual(question_data['responses'][0].response_text, "Django is a web framework.")

    def test_exercise_detail_view_unauthenticated_user(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in'))

    def test_exercise_detail_view_without_user_profile(self):
        """Test that a logged-in user without a profile is redirected to the dashboard."""
        new_user = User.objects.create_user(
            username='anotheruser', 
            password='anotherpassword', 
            email='anotheruser@example.com'
        )
        self.client.login(username='anotheruser', password='anotherpassword')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(response.url.startswith('/dashboard'))

