from django.test import TestCase, Client
from django.urls import reverse
from users.models import EndUser, User, UserProgramEnrollment, UserModuleEnrollment, UserModuleProgress
from client.models import Program, Module, ProgramModule

class DashboardViewTest(TestCase):
    def setUp(self):
        """Set up test data before each test case."""
        self.client = Client()

        # Create a test user and EndUser profile
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.end_user = EndUser.objects.create(user=self.user, age=25, gender="female", last_time_to_work="1_year", sector="it")

        # Create a test program and modules
        self.program = Program.objects.create(title="Test Program")
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.module3 = Module.objects.create(title="Outside Module 1")
        self.module4 = Module.objects.create(title="Outside Module 2")

        # Assign modules to the program with an order
        self.program_module1 = ProgramModule.objects.create(program=self.program, module=self.module1, order=1)
        self.program_module2 = ProgramModule.objects.create(program=self.program, module=self.module2, order=2)

        # Enroll user in the program
        self.enrollment = UserProgramEnrollment.objects.create(user=self.end_user, program=self.program)

        # Track user progress on the first module (inside the program)
        self.module_progress = UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=50.0)

        # Enroll the user in outside modules
        self.outside_enrollment1 = UserModuleEnrollment.objects.create(user=self.end_user, module=self.module3)
        self.outside_enrollment2 = UserModuleEnrollment.objects.create(user=self.end_user, module=self.module4)
        
        # Track progress for an outside module
        self.module_progress_outside = UserModuleProgress.objects.create(user=self.end_user, module=self.module3, completion_percentage=75.0)
        
        # Dashboard URL
        self.dashboard_url = reverse("dashboard")

    def test_dashboard_loads_for_authenticated_user(self):
        """Test if an authenticated user can access the dashboard."""
        self.client.login(username="testuser", password="testpass")  # Login as test user
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)  # Dashboard should be accessible
        self.assertTemplateUsed(response, "users/dashboard.html")  # Correct template should be used

    def test_dashboard_redirects_for_anonymous_user(self):
        """Test if an unauthenticated user is redirected to the login page."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        
        from django.conf import settings
        expected_login_url = settings.LOGIN_URL if hasattr(settings, "LOGIN_URL") else "/accounts/login/"
        self.assertTrue(response.url.startswith(expected_login_url))

    def test_dashboard_context_data(self):
        """Test if the correct data is passed to the template context."""
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.dashboard_url)
        context = response.context

        # Validate user and program contexts
        self.assertEqual(context["user"], self.user)
        self.assertEqual(context["program"], self.program)

        # Validate program modules
        program_modules = context["program_modules"]
        actual_modules = [pm.module for pm in program_modules]

        self.assertIn(self.module1, actual_modules)
        self.assertIn(self.module2, actual_modules)

        # Validate progress for program modules
        module1_context = next((m for m in actual_modules if m.id == self.module1.id), None)
        self.assertIsNotNone(module1_context)
        self.assertEqual(module1_context.progress_value, 50.0)
        self.assertTrue(module1_context.is_unlocked)  # Should be unlocked because it's the first module

        module2_context = next((m for m in actual_modules if m.id == self.module2.id), None)
        self.assertIsNotNone(module2_context)
        self.assertEqual(module2_context.progress_value, 0.0)
        self.assertFalse(module2_context.is_unlocked)  # Should be locked because module1 is not completed

        # Validate outside modules (they should include progress_value)
        outside_modules = context["outside_modules"]
        module3_context = next((m for m in outside_modules if m.id == self.module3.id), None)
        module4_context = next((m for m in outside_modules if m.id == self.module4.id), None)

        self.assertIsNotNone(module3_context)
        self.assertEqual(module3_context.progress_value, 75.0)  # This module has 75% progress

        self.assertIsNotNone(module4_context)
        self.assertEqual(module4_context.progress_value, 0.0)  # This module has no progress tracked yet

        # Validate recent modules
        recent_modules = context["recent_modules"]
        self.assertIn(self.module3, recent_modules)

        # Validate program progress value
        self.assertIn("program_progress_value", context)

