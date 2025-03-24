from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, AdditionalResource
from users.models import EndUser
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class AddAdditionalResourceViewTest(TestCase):
    """Test suite for the add_additional_resource view."""
    
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        # Create an admin user
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='admin@example.com', password='adminpass'
        )
        EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")
        
        # Create a normal user
        cls.normal_user = User.objects.create_user(
            username='normaluser', email='normal@example.com', password='normalpass'
        )
        EndUser.objects.create(user=cls.normal_user, age=30, gender="female", sector="healthcare")
        
        # Create a Module
        cls.module = Module.objects.create(title="Test Module", description="A test module")
        
        # URL for the view
        cls.url = reverse('add_additional_resource')
        cls.url_with_module = f"{cls.url}?module_id={cls.module.id}&next=/all_modules/"

    def test_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to the login page."""
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)
        
    def test_access_denied_for_non_admin_user(self):
        """Test that non-admin users cannot access the view."""
        self.client.login(username='normaluser', password='normalpass')
        response = self.client.get(self.url)
        expected_url = reverse('log_in') + "?next=" + self.url
        self.assertRedirects(response, expected_url)

    def test_admin_user_can_access(self):
        """Test that an admin user can access the add additional resource page."""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/add_additional_resource.html")

    def test_admin_user_can_add_resource(self):
        """Test successful addition of a resource by an admin."""
        self.client.login(username='adminuser', password='adminpass')
        
        file = SimpleUploadedFile("testfile.pdf", b"Dummy content", content_type="application/pdf")
        
        response = self.client.post(self.url, {
            'title': 'Test Resource',
            'description': 'Resource description',
            'resource_type': 'pdf',
            'file': file,
        }, follow=True)
        
        self.assertEqual(AdditionalResource.objects.count(), 1)
        resource = AdditionalResource.objects.first()
        self.assertEqual(resource.title, 'Test Resource')
        self.assertEqual(resource.resource_type, 'pdf')

    def test_admin_user_can_link_resource_to_module(self):
        """Test successful linking of a resource to a module by an admin."""
        self.client.login(username='adminuser', password='adminpass')
        
        file = SimpleUploadedFile("testfile.pdf", b"Dummy content", content_type="application/pdf")
        
        response = self.client.post(self.url_with_module, {
            'title': 'Linked Resource',
            'description': 'Resource linked to module',
            'resource_type': 'pdf',
            'file': file,
        }, follow=True)
        
        self.assertEqual(AdditionalResource.objects.count(), 1)
        resource = AdditionalResource.objects.first()
        
        # Check if the resource is linked to the module
        self.assertIn(resource, self.module.additional_resources.all())
        
    def test_invalid_form_submission(self):
        """Test that an invalid form submission re-renders the form with errors."""
        self.client.login(username='adminuser', password='adminpass')
        
        response = self.client.post(self.url, {
            'description': 'No title here.',  # Missing required 'title'
            'resource_type': 'pdf'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')  # Check for error message
