from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Section
from users.models import EndUser
import json

User = get_user_model()

class GetSectionsViewTest(TestCase):
    """Test suite for the get_sections view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        
        # Create an admin user and associated profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='user@example.com', password='userpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # Create some sections
        cls.section1 = Section.objects.create(title="Section 1")
        cls.section2 = Section.objects.create(title="Section 2")
        
        # URL for the view
        cls.url = reverse('get_sections')

    def test_redirect_if_not_logged_in(self):
        """Test if unauthenticated users are redirected to the login page"""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that non-admin users are denied access"""
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_user_can_access(self):
        """Test that an admin user can access the view and get sections as JSON"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse JSON response
        response_data = json.loads(response.content)
        
        # Check if the correct sections are returned
        sections = response_data['sections']
        section_titles = [section['title'] for section in sections]
        
        self.assertIn('Section 1', section_titles)
        self.assertIn('Section 2', section_titles)
        self.assertEqual(len(sections), 2)
