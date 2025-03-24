from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, ExerciseQuestion
from users.models import EndUser
import json

User = get_user_model()

class UpdateExerciseViewTest(TestCase):
    """Test suite for the update_exercise view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create an admin user and profile
        
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")

        # Create an exercise
        cls.exercise = Exercise.objects.create(title="Original Exercise Title")
        cls.exercise_question = ExerciseQuestion.objects.create(question_text="Original Question")
        cls.exercise.questions.add(cls.exercise_question)
        
        # URL for updating exercise
        cls.url = reverse('update_exercise', args=[cls.exercise.id])

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page"""
        response = self.client.post(self.url, json.dumps({
            "title": "New Title",
            "questions": [{"text": "New Question"}]
        }), content_type="application/json")
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a non-admin user is denied access"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(self.url, json.dumps({
            "title": "New Title",
            "questions": [{"text": "New Question"}]
        }), content_type="application/json")
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_can_update_exercise(self):
        """Test that an admin user can update an exercise and add questions"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, json.dumps({
            "title": "Updated Exercise Title",
            "questions": [{"text": "New Question 1"}, {"text": "New Question 2"}]
        }), content_type="application/json")

        # Refresh from the database
        self.exercise.refresh_from_db()

        # Check if the title was updated
        self.assertEqual(self.exercise.title, "Updated Exercise Title")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Exercise updated successfully!"})

        # Check if the new questions were added to the exercise
        self.assertEqual(self.exercise.questions.count(), 3)
        self.assertTrue(self.exercise.questions.filter(question_text="New Question 1").exists())
        self.assertTrue(self.exercise.questions.filter(question_text="New Question 2").exists())
    
    def test_invalid_exercise_id(self):
        """Test trying to update an exercise with an invalid ID"""
        self.client.login(username='adminuser', password='adminpass')
        invalid_url = reverse('update_exercise', args=[9999])

        response = self.client.post(invalid_url, json.dumps({
            "title": "Nonexistent Exercise",
            "questions": [{"text": "Random Question"}]
        }), content_type="application/json")

        # ✅ Check if the response code is 404
        self.assertEqual(response.status_code, 404)

        # ✅ Check if the response content matches what we expect
        self.assertJSONEqual(response.content, {"success": False, "error": "Exercise not found."})


    def test_missing_title(self):
        """Test that title is not changed if not provided in the request"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, json.dumps({
            "questions": [{"text": "New Question 3"}]
        }), content_type="application/json")

        self.exercise.refresh_from_db()

        # Check that the title was not updated
        self.assertEqual(self.exercise.title, "Original Exercise Title")
        self.assertEqual(self.exercise.questions.count(), 2)  # Existing question + New one

    def test_duplicate_question(self):
        """Test that duplicate questions are not added"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, json.dumps({
            "questions": [{"text": "Original Question"}, {"text": "Original Question"}]
        }), content_type="application/json")

        self.exercise.refresh_from_db()
        
        # Check if the original question wasn't duplicated
        self.assertEqual(self.exercise.questions.count(), 1)
        self.assertJSONEqual(response.content, {"success": True, "message": "Exercise updated successfully!"})
