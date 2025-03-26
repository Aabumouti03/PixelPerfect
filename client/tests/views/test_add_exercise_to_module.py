from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, Exercise, Section
from users.models import EndUser
import json

User = get_user_model()

class AddExerciseToModuleTest(TestCase):
    """Test suite for the add_exercise_to_module view."""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create admin user and profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=30, gender='male', sector='IT')
        
        # Create a module and an exercise
        cls.module = Module.objects.create(title='Test Module', description='Testing Module Description')
        cls.exercise = Exercise.objects.create(title='Sample Exercise', exercise_type='short_answer')
        
        # URL for the view
        cls.url = reverse('add_exercise_to_module', args=[cls.module.id])

    def test_add_exercise_to_module_success(self):
        """Test successfully adding an exercise to a module."""
        self.client.login(username='adminuser', password='adminpass')

        response = self.client.post(self.url, 
            json.dumps({'exercise_id': self.exercise.id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'success': True})

        # Check if the section was created and the exercise added
        section_title = f"{self.module.title} - General Exercises"
        section = Section.objects.get(title=section_title)
        self.assertIn(self.exercise, section.exercises.all())
        self.assertIn(section, self.module.sections.all())

    def test_missing_exercise_id(self):
        """Test request with missing exercise_id."""
        self.client.login(username='adminuser', password='adminpass')

        response = self.client.post(self.url, 
            json.dumps({}),  # No exercise_id provided
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Missing exercise ID'})

    def test_nonexistent_exercise(self):
        """Test trying to add a non-existent exercise."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url, 
            json.dumps({'exercise_id': 9999}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        error_message = response.json().get('error', '')
        self.assertIn("Exercise", error_message)



    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the view."""
        response = self.client.post(self.url, 
            json.dumps({'exercise_id': self.exercise.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 302)  # Redirects to login page

    def test_invalid_request_method(self):
        """Test invalid request method (GET)."""
        self.client.login(username='adminuser', password='adminpass')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'success': False, 'error': 'Invalid request method'})
