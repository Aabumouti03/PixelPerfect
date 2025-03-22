from django.test import TestCase, Client
from django.urls import reverse

class StaticUserPageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_modules_view(self):
        """Should render the modules page successfully."""
        response = self.client.get(reverse('modules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/modules.html')

    def test_profile_view(self):
        """Should render the profile page successfully."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_welcome_view(self):
        """Should render the welcome page successfully."""
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/welcome.html')