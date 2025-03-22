from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser, UserProgramEnrollment, UserModuleProgress
from client.models import Program, Module, ProgramModule

class ViewProgramTest(TestCase):
    """Tests for the view_program view"""

    def setUp(self):
        """Set up a user, program, and modules before each test"""
        User = get_user_model()

        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.login(username="testuser", password="password123")
        self.program = Program.objects.create(title="Test Program", description="A test program")

        # Create modules and link them to the program with an order
        self.module1 = Module.objects.create(title="Module 1", description="First module")
        self.module2 = Module.objects.create(title="Module 2", description="Second module")

        self.program_module1 = ProgramModule.objects.create(program=self.program, module=self.module1, order=1)
        self.program_module2 = ProgramModule.objects.create(program=self.program, module=self.module2, order=2)

        # Enroll user in the program
        self.end_user = EndUser.objects.create(user=self.user, age=25, gender="female", sector="it")
        self.enrollment = UserProgramEnrollment.objects.create(user=self.end_user, program=self.program)

        # Create progress records
        UserModuleProgress.objects.create(user=self.end_user, module=self.module1, completion_percentage=100)
        UserModuleProgress.objects.create(user=self.end_user, module=self.module2, completion_percentage=50)

        self.program_url = reverse("view_program", args=[self.program.id])

    def test_authenticated_user_can_access_program(self):
        """Test that an authenticated user enrolled in a program can access it"""
        response = self.client.get(self.program_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Program")  # Program title is shown
        self.assertContains(response, "Module 1")      # Module 1 is listed
        self.assertContains(response, "Module 2")      # Module 2 is listed

    def test_user_with_no_enduser_record(self):
        """Test when user has no corresponding EndUser record"""
        # Delete the EndUser record
        self.end_user.delete()
        
        response = self.client.get(self.program_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/program_not_found.html')

    def test_authenticated_user_not_enrolled_sees_not_found_page(self):
        """Test that an authenticated user not enrolled in the program gets a not found page"""
        # Try accessing a different program the user is not enrolled in
        new_program = Program.objects.create(title="Other Program", description="Another test program")
        response = self.client.get(reverse("view_program", args=[new_program.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/program_not_found.html")

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that an unauthenticated user is redirected to login"""
        self.client.logout()
        response = self.client.get(self.program_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("log_in")))


    def test_modules_are_ordered_correctly(self):
        """Test that program modules are ordered correctly"""
        response = self.client.get(self.program_url)

        modules = response.context["program_modules"]
        self.assertEqual(modules[0]["title"], "Module 1")
        self.assertEqual(modules[1]["title"], "Module 2")

    def test_module_progress_values(self):
        """Test that progress values are assigned correctly"""
        response = self.client.get(self.program_url)

        modules = response.context["program_modules"]
        self.assertEqual(modules[0]["progress_value"], 100)  # Module 1 completed
        self.assertEqual(modules[1]["progress_value"], 50)   # Module 2 at 50%

    def test_module_locking_logic(self):
        """Test that modules are locked/unlocked based on progress"""
        response = self.client.get(self.program_url)

        modules = response.context["program_modules"]
        self.assertFalse(modules[0]["locked"])  # First module should be unlocked
        self.assertFalse(modules[1]["locked"])  # Second module should also be unlocked

        # Now, reset progress for module1 and re-run the test
        UserModuleProgress.objects.filter(module=self.module1).update(completion_percentage=0)
        response = self.client.get(self.program_url)

        modules = response.context["program_modules"]
        self.assertFalse(modules[0]["locked"])  # First module should still be unlocked
        self.assertTrue(modules[1]["locked"])   # Second module should now be locked
