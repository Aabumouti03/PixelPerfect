from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, Section
from users.models import EndUser
import json

User = get_user_model()

class AddExerciseToSectionViewTest(TestCase):
    """Test suite for the add_exercise_to_section view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        

        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")

        # Create a Section and an Exercise
        cls.section = Section.objects.create(title="Test Section")
        cls.exercise = Exercise.objects.create(title="Test Exercise")

        # URL for the view
        cls.url = reverse('add_exercise_to_section', args=[cls.section.id])

    def test_redirect_if_not_logged_in(self):
        """Test if unauthenticated users are redirected to the login page"""
        response = self.client.post(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a non-admin user is redirected to the login page"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.post(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_add_exercise_to_section(self):
        """Test that an admin can successfully add an exercise to a section via AJAX"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            data=json.dumps({"exercise_id": self.exercise.id}),
            content_type="application/json"
        )

        # Refresh the section from the database
        self.section.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.exercise, self.section.exercises.all())
        self.assertJSONEqual(response.content, {"success": True, "message": "Exercise added successfully!"})

    def test_invalid_exercise_id(self):
        """Test that providing an invalid exercise_id returns an error"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            data=json.dumps({"exercise_id": 9999}),  # Non-existent exercise
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {"success": False, "error": "No Exercise matches the given query."})

    def test_invalid_request_method(self):
        """Test that a GET request returns a 400 error"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request"})
