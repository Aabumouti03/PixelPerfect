from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, ExerciseQuestion
from users.models import EndUser
import json

User = get_user_model()

class DeleteExerciseQuestionsViewTest(TestCase):
    """Test suite for the delete_exercise_questions view"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # ✅ Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass"
        )
        EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # ✅ Create a regular user
        cls.normal_user = User.objects.create_user(
            username="normaluser", email="user@example.com", password="userpass"
        )
        EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # ✅ Create an exercise and some questions
        cls.exercise = Exercise.objects.create(title="Sample Exercise")
        cls.question1 = ExerciseQuestion.objects.create(question_text="What is Django?")
        cls.question2 = ExerciseQuestion.objects.create(question_text="Explain MVC.")
        
        # ✅ Link questions to the exercise
        cls.exercise.questions.add(cls.question1, cls.question2)
        
        # ✅ Define the URL
        cls.url = reverse('delete_exercise_questions', args=[cls.exercise.id])

        def test_admin_can_delete_questions(self):
            """Test successful deletion of questions by an admin"""
            self.client.login(username='adminuser', password='adminpass')
            
            self.exercise.questions.add(self.question1)
            
            response = self.client.post(self.url, json.dumps({
                "question_ids": [self.question1.id]
            }), content_type="application/json")
            
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, {"success": True, "message": "1 questions deleted!"})
            
            self.assertFalse(ExerciseQuestion.objects.filter(id=self.question1.id).exists())
            self.assertTrue(ExerciseQuestion.objects.filter(id=self.question2.id).exists())


    def test_non_admin_user_cannot_delete_questions(self):
        """Test that non-admin users cannot delete questions"""
        self.client.login(username='normaluser', password='userpass')
        
        response = self.client.post(self.url, json.dumps({
            "question_ids": [self.question1.id]
        }), content_type="application/json")
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_invalid_question_ids(self):
        """Test attempting to delete non-existent questions"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({
            "question_ids": [9999]
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "0 questions deleted!"})

    def test_no_questions_selected(self):
        """Test when no question IDs are provided in the request"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, json.dumps({
            "question_ids": []
        }), content_type="application/json")
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "No questions selected"})

    def test_invalid_request_method(self):
        """Test using a GET request instead of POST"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request"})
