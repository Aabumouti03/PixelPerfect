from django.test import TestCase
from django.urls import reverse
from users.models import User 
from client.models import Exercise, Section, ExerciseQuestion
from users.models import EndUser
from django.core.files.uploadedfile import SimpleUploadedFile

class ExerciseDetailViewTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        
        # Create an Exercise with a question
        self.exercise = Exercise.objects.create(title="Test Exercise", exercise_type="short_answer")
        
        # Create a question for the exercise
        self.question = ExerciseQuestion.objects.create(question_text="What is 2 + 2?")
        self.exercise.questions.add(self.question)

        # Create a Section with a diagram and add to the exercise
        section = Section.objects.create(title="Section 1", description="Description for section 1")
        section.exercises.add(self.exercise)
        section.diagram = SimpleUploadedFile(name="test_diagram.png", content=b"file_content", content_type="image/png")
        section.save()

        # Create EndUser for the logged-in user
        self.end_user = EndUser.objects.create(user=self.user)

        # Log the user in
        self.client.login(username="testuser", password="testpassword")
    

    def test_get_exercise_detail(self):
        # The URL to test
        url = reverse('exercise_detail', kwargs={'exercise_id': self.exercise.id})

        # Perform GET request
        response = self.client.get(url)

        # Check the response status
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'users/exercise_detail.html')

        # Check that the exercise is in the context
        self.assertIn('exercise', response.context)
        self.assertEqual(response.context['exercise'], self.exercise)

        # Check that the diagram is in the context
        self.assertIn('diagram', response.context)

        # Corrected line: use the section variable from setUp
        section = self.exercise.sections.first()  # Get the first section of the exercise
        self.assertEqual(response.context['diagram'], section.diagram)  # Compare to the diagram from the section


    def test_post_exercise_detail(self):
        # The URL to test
        url = reverse('exercise_detail', kwargs={'exercise_id': self.exercise.id})

        # Simulate posting an answer for the question
        response = self.client.post(url, data={f'answer_{self.question.id}': '4'})

        # Check the response status after posting
        self.assertEqual(response.status_code, 302)  # Should redirect after POST request

        # Check that the URL after redirect is correct
        self.assertRedirects(response, reverse('exercise_detail', kwargs={'exercise_id': self.exercise.id}))


    def test_no_diagram_in_section(self):
        # Create a section without a diagram
        section_no_diagram = Section.objects.create(title="Section Without Diagram", description="No diagram here")
        section_no_diagram.exercises.add(self.exercise)

        # Perform GET request to exercise detail
        url = reverse('exercise_detail', kwargs={'exercise_id': self.exercise.id})
        response = self.client.get(url)

        # Check that no diagram is passed to the template
        self.assertIsNone(response.context['diagram'])  # Since there's no diagram
