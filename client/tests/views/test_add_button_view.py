from django.test import TestCase, Client
from django.urls import reverse
from client.models import Module
from users.models import User, EndUser  # Import your custom User model

class AddButtonViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        
        # Create a superuser for testing (admin)
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        self.end_user = EndUser.objects.create(user=self.admin_user)  # Creating a related EndUser instance
        self.url = reverse('add_module')

    def test_add_button_view_redirects_for_anonymous_user(self):
        """Test that anonymous users are redirected to the login page."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('log_in')))  # Check against your custom login URL

    def test_add_button_view_forbidden_for_non_admin_user(self):
        """Test that non-admin users cannot access the view."""
        # Create a regular user
        regular_user = User.objects.create_user(
            username='regularuser',
            password='regularpass',
            email='user@example.com'
        )
        self.client.login(username='regularuser', password='regularpass')
        
        response = self.client.get(self.url)
        
        # Check for a redirect if using `login_url` in `user_passes_test`
        self.assertEqual(response.status_code, 403)  # Change to 302 if you're not forcing 403
        

    def test_add_button_view_get_request(self):
        """Test GET request renders the add_module.html template."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Module/add_module.html')

    def test_add_button_view_post_request_success(self):
        """Test POST request successfully creates a Module."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {
            'title': 'New Test Module',
            'description': 'This is a test description for a module.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('client_modules'))
        
        module = Module.objects.filter(title='New Test Module').first()
        self.assertIsNotNone(module)
        self.assertEqual(module.title, 'New Test Module')
        self.assertEqual(module.description, 'This is a test description for a module.')

    def test_add_button_view_forbidden_for_non_admin_user(self):
        """Test that non-admin users cannot access the view."""
        # Create a regular user
        regular_user = User.objects.create_user(
            username='regularuser',
            password='regularpass',
            email='user@example.com'
        )
        self.client.login(username='regularuser', password='regularpass')
        
        response = self.client.get(self.url)
        
        # Test for redirect if non-admin user tries to access the view
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('log_in')))  # Or wherever you redirect unauthorized users

