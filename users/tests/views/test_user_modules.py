from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, UserModuleEnrollment, UserModuleProgress
from client.models import Module

class UserModulesViewTest(TestCase):
    def setUp(self):
        User = get_user_model()  
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.end_user, _ = EndUser.objects.get_or_create(user=self.user)
        self.module = Module.objects.create(title="Test Module", description="Test Description")
        self.enrollment = UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)
        self.progress = UserModuleProgress.objects.create(user=self.end_user, module=self.module, completion_percentage=50)

    def test_user_modules_no_progress(self):
        """Test that a module with no progress defaults to 0% progress."""
        self.progress.delete()  
        response = self.client.get(reverse('userModules'))
        # Expect the inline style to show "0%;" (numeric formatting without decimal)
        self.assertContains(response, 'style="width: 0%;"')
        # Update expected text to match the template output ("Complete" with capital C)
        self.assertContains(response, '0% Complete')

    def test_user_modules_multiple_enrollments(self):
        """Test that multiple enrolled modules are displayed correctly."""
        module2 = Module.objects.create(title="Another Module", description="Another Description")
        UserModuleEnrollment.objects.create(user=self.end_user, module=module2)
        response = self.client.get(reverse('userModules'))
        self.assertContains(response, "Test Module")
        self.assertContains(response, "Another Module")

    def test_redirect_if_not_logged_in(self):
        """Ensure unauthenticated users are redirected to login."""
        self.client.logout()
        response = self.client.get(reverse('userModules'))
        expected_url = f"{reverse('log_in')}?next={reverse('userModules')}"
        self.assertRedirects(response, expected_url)

    def test_user_modules_no_enrollments(self):
        """Test that if the user is not enrolled in any modules, module_data is empty."""
        UserModuleEnrollment.objects.filter(user=self.end_user).delete()
        response = self.client.get(reverse('userModules'))
        self.assertEqual(len(response.context.get('module_data', [])), 0)
        # Optionally, assert that a "no modules" message is rendered if applicable

    def test_user_modules_update_progress(self):
        """Test that updating progress reflects correctly in the rendered page."""
        self.progress.completion_percentage = 75
        self.progress.save()
        response = self.client.get(reverse('userModules'))
        # The template will render the updated progress as "75.0%;" if it's a float
        self.assertContains(response, 'style="width: 75.0%;"')
        self.assertContains(response, '75.0% Complete')

    def test_end_user_creation(self):
        """Test that if an EndUser object does not exist for a logged-in user, it is created by the view."""
        self.end_user.delete()  # Remove the existing EndUser
        response = self.client.get(reverse('userModules'))
        new_end_user = EndUser.objects.get(user=self.user)
        self.assertIsNotNone(new_end_user)
        self.assertEqual(len(response.context.get('module_data', [])), 0)

    def test_context_data_structure(self):
        """Test that the context data for modules includes the expected keys."""
        response = self.client.get(reverse('userModules'))
        module_data = response.context.get('module_data', [])
        self.assertGreaterEqual(len(module_data), 1)
        for module in module_data:
            # Update expected key from 'progress' to 'progress_value'
            self.assertIn('id', module)
            self.assertIn('title', module)
            self.assertIn('description', module)
            self.assertIn('progress_value', module)
