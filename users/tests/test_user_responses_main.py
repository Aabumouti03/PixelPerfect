from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Exercise  # Adjust this import path to your actual model location

User = get_user_model()

class UserResponsesMainViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.url = reverse("user_responses_main")

        # Create some exercises
        self.exercise1 = Exercise.objects.create(title="Exercise 1")
        self.exercise2 = Exercise.objects.create(title="Exercise 2")

    def test_redirect_if_not_logged_in(self):
        """Unauthenticated users should be redirected to login page."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}')

    def test_logged_in_user_sees_exercises(self):
        """Logged-in users should see exercises on the page."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "UserResponce/user_responses_main.html")
        self.assertContains(response, "Exercise 1")
        self.assertContains(response, "Exercise 2")

    def test_view_with_no_exercises(self):
        Exercise.objects.all().delete()
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Exercise 1")
