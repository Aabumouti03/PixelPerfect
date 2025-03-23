from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise, Section
from users.models import EndUser
from client.forms import ExerciseForm

User = get_user_model()

class EditExerciseViewTest(TestCase):
    """Test suite for the edit_exercise view"""
    
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
        
        # Create a section and an exercise
        cls.section = Section.objects.create(title="Test Section")
        cls.exercise = Exercise.objects.create(title="Original Exercise Title")
        
        # Associate the exercise with the section
        cls.exercise.sections.add(cls.section)
        
        # URL for the view
        cls.url = reverse('edit_exercise', args=[cls.exercise.id])

    def test_redirect_if_not_logged_in(self):
        """Test if an unauthenticated user is redirected to the login page"""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that a non-admin user is denied access"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_user_can_access(self):
        """Test that an admin user can access the edit exercise view"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        # ✅ Check if the response is successful
        self.assertEqual(response.status_code, 200)
        
        # ✅ Check if the correct template is used
        self.assertTemplateUsed(response, 'Module/manage_exercises.html')


    def test_non_existent_exercise(self):
        """Test that accessing a non-existent exercise returns a 404 error"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('edit_exercise', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_successful_exercise_edit(self):
        """Test that an admin can successfully edit an exercise"""
        self.client.login(username='adminuser', password='adminpass')
        
        # ✅ Make sure we pass the required fields for the ExerciseForm
        response = self.client.post(self.url, {
            'title': 'Updated Exercise Title',
            'exercise_type': 'short_answer',  # Make sure to specify a valid exercise type
        })
        
        # 🔄 Refresh the exercise instance from the database
        self.exercise.refresh_from_db()
        
        # ✅ Check if the title was updated successfully
        self.assertEqual(self.exercise.title, 'Updated Exercise Title')
        self.assertRedirects(response, reverse('edit_section', args=[self.section.id]))



