from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, ExerciseQuestion
from users.models import EndUser
import json

User = get_user_model()

class AddExerciseAjaxViewTest(TestCase):
    """Test suite for the add_exercise_ajax view."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # URL for the view
        cls.url = reverse('add_exercise_ajax')

    def test_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page"""
        response = self.client.post(self.url, json.dumps({
            "title": "New Exercise",
            "questions": ["What is Django?", "Explain ORM."]
        }), content_type="application/json")
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin_user(self):
        """Test that non-admin users are redirected"""
        normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        EndUser.objects.create(user=normal_user, age=30, gender="female", sector="healthcare")

        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(self.url, json.dumps({
            "title": "New Exercise",
            "questions": ["What is Django?", "Explain ORM."]
        }), content_type="application/json")
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)
    
    def test_missing_title(self):
        """Test that missing title returns an error"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, json.dumps({
            "questions": ["What is Django?", "Explain ORM."]
        }), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Title is required"})

    def test_successful_exercise_creation(self):
        """Test successful creation of an exercise with questions"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({
            "title": "New Exercise",
            "questions": ["What is Django?", "Explain ORM."]
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # ✅ Check the response success
        self.assertTrue(response_data["success"])
        self.assertIn("exercise_id", response_data)
        
        # ✅ Check that the exercise is saved in the database
        exercise_id = response_data["exercise_id"]
        exercise = Exercise.objects.get(id=exercise_id)
        self.assertEqual(exercise.title, "New Exercise")
        self.assertEqual(exercise.questions.count(), 2)
        
        # ✅ Verify the questions were saved correctly
        question_texts = exercise.questions.values_list('question_text', flat=True)
        self.assertIn("What is Django?", question_texts)
        self.assertIn("Explain ORM.", question_texts)

    def test_exercise_creation_with_no_questions(self):
        """Test creating an exercise without questions"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({
            "title": "Questionless Exercise",
            "questions": []
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        
        # ✅ Check the response success
        self.assertTrue(response_data["success"])
        self.assertIn("exercise_id", response_data)
        
        # ✅ Check that the exercise is saved in the database
        exercise_id = response_data["exercise_id"]
        exercise = Exercise.objects.get(id=exercise_id)
        self.assertEqual(exercise.title, "Questionless Exercise")
        self.assertEqual(exercise.questions.count(), 0)

    def test_invalid_json_request(self):
        """Test handling of invalid JSON data"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, data="Invalid JSON", content_type="application/json")
        
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["success"])
        self.assertIn("error", response_data)
