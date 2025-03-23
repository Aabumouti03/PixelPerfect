from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Section, Exercise
from users.models import EndUser
from client.forms import SectionForm

User = get_user_model()

class AddSectionViewTest(TestCase):
    """Test suite for the add_section view"""

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

        # Create some exercises to be used in the section
        cls.exercise1 = Exercise.objects.create(title="Exercise 1")
        cls.exercise2 = Exercise.objects.create(title="Exercise 2")

        # URL for the view
        cls.url = reverse('add_section')

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
        """Test that an admin user can access the add section view"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_section.html')
        self.assertIsInstance(response.context['form'], SectionForm)

    def test_successful_section_creation(self):
        """Test successful creation of a section by an admin"""
        self.client.login(username='adminuser', password='adminpass')

        # ✅ Submit POST data to create a section
        response = self.client.post(self.url, {
            'title': 'New Section',
            'description': 'This is a test section.',
        }, follow=True)

        # ✅ Ensure redirection to the 'add_module' view
        self.assertRedirects(response, reverse('add_module'))

        # ✅ Check if the section was saved in the database
        self.assertTrue(Section.objects.filter(title='New Section').exists())

        # ✅ Verify the content of the created section
        section = Section.objects.get(title='New Section')
        self.assertEqual(section.description, 'This is a test section.')

    def test_invalid_section_submission(self):
        """Test submission of an invalid form"""
        self.client.login(username='adminuser', password='adminpass')

        # Submit POST data with missing title
        response = self.client.post(self.url, {
            'description': 'This is a section without a title.'
        }, follow=True)

        # The response should render the same form with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_section.html')
        self.assertTrue(response.context['form'].errors)

    def test_exercises_available_in_context(self):
        """Test that exercises are available in the context for selection"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        
        # Check if exercises are correctly passed in the context
        available_exercises = response.context['exercises']
        self.assertIn(self.exercise1, available_exercises)
        self.assertIn(self.exercise2, available_exercises)
