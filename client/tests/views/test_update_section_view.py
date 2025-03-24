from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Section
from users.models import EndUser
import json

User = get_user_model()

class UpdateSectionViewTest(TestCase):
    """Test suite for the update_section view"""

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

        # Create a Section
        cls.section = Section.objects.create(title="Original Title", description="Original Description")

        # URL for the view
        cls.url = reverse('update_section', args=[cls.section.id])

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

    def test_update_section_title(self):
        """Test that an admin can successfully update the section title via AJAX"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            data=json.dumps({"field": "title", "value": "Updated Title"}),
            content_type="application/json"
        )

        # Refresh the section from the database
        self.section.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.section.title, "Updated Title")
        self.assertJSONEqual(response.content, {"success": True})

    def test_update_section_description(self):
        """Test that an admin can successfully update the section description via AJAX"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            data=json.dumps({"field": "description", "value": "Updated Description"}),
            content_type="application/json"
        )

        # Refresh the section from the database
        self.section.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.section.description, "Updated Description")
        self.assertJSONEqual(response.content, {"success": True})

    def test_invalid_field(self):
        """Test that an invalid field returns a 400 error"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(
            self.url,
            data=json.dumps({"field": "invalid_field", "value": "Some Value"}),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid field"})

    def test_invalid_request_method(self):
        """Test that GET requests are not allowed"""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"success": False, "error": "Invalid request"})
