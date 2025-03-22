from django.test import TestCase, Client
from django.urls import reverse
from users.models import EndUser, UserModuleEnrollment
from client.models import Module
from django.contrib.auth import get_user_model

User = get_user_model()

class AllModulesPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.module1 = Module.objects.create(title="Module 1", description="Description 1")
        self.module2 = Module.objects.create(title="Module 2", description="Description 2")

        # Create EndUser profile
        self.end_user = EndUser.objects.create(user=self.user)

        # Enroll the user in one module
        UserModuleEnrollment.objects.create(user=self.end_user, module=self.module1)

        self.all_modules_url = reverse('all_modules')

    # Test that the page loads correctly
    def test_all_modules_view(self):
        response = self.client.get(self.all_modules_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.module1.title)
        self.assertContains(response, self.module2.title)

    # Test that the page requires login
    def test_all_modules_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.all_modules_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    # Test that all modules are listed correctly
    def test_all_modules_shows_correct_modules(self):
        response = self.client.get(self.all_modules_url)
        self.assertContains(response, "Module 1")
        self.assertContains(response, "Module 2")
        self.assertContains(response, "Description 1")
        self.assertContains(response, "Description 2")

    # Test that enrolled modules are marked correctly
    def test_all_modules_marks_enrolled_modules(self):
        response = self.client.get(self.all_modules_url)
        self.assertContains(response, "Module 1")  # Enrolled module
        self.assertContains(response, "Module 2")  # Not enrolled, but listed

        # Ensure enrolled module is marked in the template
        enrolled_modules = response.context['enrolled_modules']
        self.assertIn("Module 1", enrolled_modules)
        self.assertNotIn("Module 2", enrolled_modules)

    # Test the empty state (no modules)
    def test_all_modules_empty_state(self):
        Module.objects.all().delete()
        response = self.client.get(self.all_modules_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Module 1")
        self.assertNotContains(response, "Module 2")

    # Test the empty state (no enrollments)
    def test_all_modules_no_enrollments(self):
        UserModuleEnrollment.objects.all().delete()
        response = self.client.get(self.all_modules_url)
        self.assertEqual(response.status_code, 200)

        # User should see available modules but not as enrolled
        self.assertContains(response, "Module 1")
        self.assertContains(response, "Module 2")
        enrolled_modules = response.context['enrolled_modules']
        self.assertEqual(len(enrolled_modules), 0)
        
    def test_all_modules_handles_missing_end_user(self):
        # Delete the EndUser to trigger the exception
        EndUser.objects.all().delete()

        response = self.client.get(self.all_modules_url)
        self.assertEqual(response.status_code, 200)

        # Check that the page loads without crashing
        self.assertContains(response, "Module 1")
        self.assertContains(response, "Module 2")

        # Since no EndUser exists, enrolled_modules should be empty
        enrolled_modules = response.context['enrolled_modules']
        self.assertEqual(len(enrolled_modules), 0)