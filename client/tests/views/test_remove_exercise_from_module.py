from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, Section, Exercise
from users.models import EndUser
import json

User = get_user_model()


class RemoveExerciseFromModuleTest(TestCase):
    """Test suite for remove_exercise_from_module view."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="adminpass"
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # Create a regular user
        cls.normal_user = User.objects.create_user(
            username="normaluser", email="user@example.com", password="userpass"
        )
        cls.normal_profile = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # Create exercises
        cls.exercise1 = Exercise.objects.create(title="Exercise 1")
        cls.exercise2 = Exercise.objects.create(title="Exercise 2")
        
        # Create section
        cls.section = Section.objects.create(title="Test Section")
        cls.section.exercises.set([cls.exercise1, cls.exercise2])
        
        # Create module and link the section
        cls.module = Module.objects.create(title="Test Module", description="Module for testing")
        cls.module.sections.add(cls.section)

        # URL to test
        cls.url = reverse('remove_exercises_from_module', args=[cls.module.id])

    def test_remove_exercise_success(self):
        """Test successfully removing exercises from a module by an admin user."""
        self.client.login(username="adminuser", password="adminpass")
        
        response = self.client.post(self.url, 
                                    data=json.dumps({"exercise_ids": [self.exercise1.id]}),
                                    content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})

        # Refresh section and verify the exercise was removed
        self.section.refresh_from_db()
        remaining_exercises = list(self.section.exercises.values_list('id', flat=True))
        self.assertNotIn(self.exercise1.id, remaining_exercises)
        self.assertIn(self.exercise2.id, remaining_exercises)

    def test_remove_invalid_exercise_id(self):
        """Test trying to remove an exercise that doesn't exist."""
        self.client.login(username="adminuser", password="adminpass")
        
        response = self.client.post(self.url, 
                                    data=json.dumps({"exercise_ids": [9999]}),
                                    content_type="application/json")
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True})  # It should return success even if the ID doesn't exist

    def test_non_admin_user_cannot_remove(self):
        """Test that a non-admin user cannot remove exercises."""
        self.client.login(username="normaluser", password="userpass")
        
        response = self.client.post(self.url, 
                                    data=json.dumps({"exercise_ids": [self.exercise1.id]}),
                                    content_type="application/json")
        
        self.assertEqual(response.status_code, 302)  # Redirect to login because of the @user_passes_test decorator

    def test_get_request_not_allowed(self):
        """Test that a GET request returns an error message."""
        self.client.login(username="adminuser", password="adminpass")
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request method."})
