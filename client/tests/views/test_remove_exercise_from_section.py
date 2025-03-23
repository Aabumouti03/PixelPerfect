from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Section, Exercise
from users.models import EndUser
import json

User = get_user_model()

class RemoveExerciseFromSectionViewTest(TestCase):
    """Test suite for the remove_exercise_from_section view"""
    
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
        
        # Create a section and exercises
        cls.section = Section.objects.create(title="Test Section")
        cls.exercise1 = Exercise.objects.create(title="Exercise 1")
        cls.exercise2 = Exercise.objects.create(title="Exercise 2")
        
        # Add exercises to the section
        cls.section.exercises.add(cls.exercise1, cls.exercise2)
        
        # URL for the view
        cls.url = reverse('remove_exercise_from_section', args=[cls.section.id])

    def test_redirect_if_not_logged_in(self):
        """Test if unauthenticated users are redirected to the login page"""
        response = self.client.post(self.url, json.dumps({"exercise_ids": [self.exercise1.id]}), content_type="application/json")
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a normal user cannot access the view"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(self.url, json.dumps({"exercise_ids": [self.exercise1.id]}), content_type="application/json")
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_successful_removal_of_exercises(self):
        """Test successful removal of exercises by admin"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url, 
            json.dumps({"exercise_ids": [self.exercise1.id]}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Exercises removed successfully!"})
        
        # Refresh section and check that exercise1 is removed
        self.section.refresh_from_db()
        self.assertNotIn(self.exercise1, self.section.exercises.all())

    def test_invalid_exercise_id(self):
        """Test trying to remove an exercise that doesn't exist"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            json.dumps({"exercise_ids": [9999]}),  # Non-existent exercise ID
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "One or more exercises do not exist."})


    def test_no_exercise_ids_provided(self):
        """Test providing an empty list of exercise_ids"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            json.dumps({"exercise_ids": []}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "No exercise IDs received."})

    def test_invalid_request_method(self):
        """Test GET request instead of POST"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request"})
