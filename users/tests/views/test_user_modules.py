from django.test import TestCase
from django.urls import reverse
from users.models import EndUser, UserModuleEnrollment, UserModuleProgress
from client.models import Module
from django.contrib.auth import get_user_model 

class UserModulesViewTest(TestCase):

    def setUp(self):
        User = get_user_model()  
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.client.login(username='testuser', password='testpassword')

        self.end_user, _ = EndUser.objects.get_or_create(user=self.user)
        self.module = Module.objects.create(title="Test Module", description="Test Description")

        self.enrollment = UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)
        self.progress = UserModuleProgress.objects.create(user=self.end_user, module=self.module, completion_percentage=50)

    def test_user_modules_view(self):
        """Test that the user modules view returns correct background color and no background image."""
        response = self.client.get(reverse('userModules'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "#ADD8E6")
        self.assertNotContains(response, "img/backgrounds/") 

    def test_user_modules_no_progress(self):
        """Test that a module with no progress defaults to 0% progress."""
        self.progress.delete()  

        response = self.client.get(reverse('userModules'))

        self.assertContains(response, 'style="width: 0%;"')
        self.assertContains(response, '0% completed')


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
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('userModules')}")
