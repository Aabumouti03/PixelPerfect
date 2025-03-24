from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module
from users.models import EndUser
import json

User = get_user_model()

class UpdateModuleViewTest(TestCase):
    """Test suite for the update_module view"""

    @classmethod
    def setUpTestData(cls):
        
        cls.client = Client()
        
        # Create an admin user and profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='adminuser@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # Create a regular user and profile
        cls.regular_user = User.objects.create_user(
            username='regularuser', email='regularuser@example.com', password='regularpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.regular_user, age=30, gender="female", sector="healthcare")
        
        # Create a sample module
        cls.module = Module.objects.create(title="Sample Module", description="Initial Description")
        cls.url = reverse('update_module', args=[cls.module.id])
        
    def test_admin_can_update_title(self):
        """Test that an admin can successfully update the module title"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'title', 'value': 'Updated Module Title'}),
            content_type='application/json'
        )
        
        self.module.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(self.module.title, 'Updated Module Title')
    
    def test_admin_can_update_description(self):
        """Test that an admin can successfully update the module description"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'description', 'value': 'Updated Description'}),
            content_type='application/json'
        )
        
        self.module.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(self.module.description, 'Updated Description')
    
    def test_non_admin_user_redirected(self):
        """Test that a non-admin user is redirected to the login page"""
        self.client.login(username='regularuser', password='regularpass')
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'title', 'value': 'Hacker Title'}),
            content_type='application/json'
        )
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)
    
    def test_invalid_field(self):
        """Test that providing an invalid field returns a 400 status code"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url,
            data=json.dumps({'field': 'invalid_field', 'value': 'Whatever'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))
    
    def test_invalid_request_method(self):
        """Test that GET requests return a 400 status code"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))
