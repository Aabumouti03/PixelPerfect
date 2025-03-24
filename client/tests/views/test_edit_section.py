from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Section, Exercise, Module
from users.models import EndUser

User = get_user_model()


class EditSectionViewTest(TestCase):
    """Test suite for the edit_section view"""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create an admin user and an EndUser profile
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='adminuser@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        # Create a regular user and an EndUser profile
        cls.regular_user = User.objects.create_user(
            username='regularuser', email='regularuser@example.com', password='regularpass'
        )
        cls.end_user = EndUser.objects.create(user=cls.regular_user, age=30, gender="female", sector="healthcare")

        # Create a sample Exercise, Module, and Section
        cls.exercise = Exercise.objects.create(title="Exercise 1")
        cls.module = Module.objects.create(title="Sample Module")
        cls.section = Section.objects.create(title="Test Section")
        
        # Associate the Section with the Module (Assuming a ForeignKey relationship)
        cls.module.sections.add(cls.section)
        
        # URL for the view
        cls.url = reverse('edit_section', args=[cls.section.id])

    def test_redirect_if_not_logged_in(self):
        """Test if unauthenticated users are redirected to the login page"""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_access_denied_for_non_admin(self):
        """Test that non-admin users are redirected to the login page"""
        self.client.login(username='regularuser', password='regularpass')
        response = self.client.get(self.url)
    
        # Compare the URL where the user is redirected to (login page with next parameter)
        expected_url = reverse("log_in") + "?next=" + self.url
        self.assertRedirects(response, expected_url)


    def test_admin_user_can_access(self):
        """Test that an admin user can access the edit section view"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/edit_section.html')

    def test_section_not_found(self):
        """Test that a 404 is returned for a non-existent section"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('edit_section', args=[999]))  # Non-existent section ID
        self.assertEqual(response.status_code, 404)

    def test_successful_section_edit(self):
        """Test that an admin can successfully edit a section"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'title': 'Updated Section Title'})
        
        # Refresh the section from the database
        self.section.refresh_from_db()
        
        self.assertEqual(self.section.title, 'Updated Section Title')
        self.assertRedirects(response, reverse('edit_module', args=[self.module.id]))  # Check if redirected correctly
