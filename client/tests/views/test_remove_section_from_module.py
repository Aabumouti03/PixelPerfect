from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, Section
from users.models import EndUser
import json

User = get_user_model()


class RemoveSectionFromModuleViewTest(TestCase):
    """Test suite for the remove_section_from_module view"""

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
        
        # Create sample module and sections
        cls.module = Module.objects.create(title="Sample Module")
        cls.section1 = Section.objects.create(title="Section 1")
        cls.section2 = Section.objects.create(title="Section 2")
        
        # Add sections to module
        cls.module.sections.add(cls.section1, cls.section2)
        
        # URL for the view
        cls.url = reverse('remove_section_from_module', args=[cls.module.id])

    def test_admin_can_remove_sections(self):
        """Test that an admin can successfully remove sections from a module"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url,
            data=json.dumps({"section_ids": [self.section1.id, self.section2.id]}),
            content_type='application/json'
        )
        
        self.module.refresh_from_db()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertNotIn(self.section1, self.module.sections.all())
        self.assertNotIn(self.section2, self.module.sections.all())
    
    def test_non_admin_user_redirected(self):
        """Test that a non-admin user is redirected to the login page"""
        self.client.login(username='regularuser', password='regularpass')
        response = self.client.post(
            self.url,
            data=json.dumps({"section_ids": [self.section1.id]}),
            content_type='application/json'
        )
        
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)
    
    def test_invalid_section_ids(self):
        """Test that invalid section IDs are handled gracefully"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url,
            data=json.dumps({"section_ids": [9999]}),  # Non-existent section ID
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
    
    def test_invalid_request_method(self):
        """Test that a GET request returns an error"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))
