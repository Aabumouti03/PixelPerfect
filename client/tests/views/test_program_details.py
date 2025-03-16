from django.test import TestCase, Client
from django.urls import reverse
from users.models import User 
from client.models import Program, Module, ProgramModule
from users.models import EndUser, UserProgramEnrollment

class ProgramDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )
        cls.end_user = EndUser.objects.create(user=cls.user)
        cls.program = Program.objects.create(title="Test Program", description="Test Description")
        cls.module1 = Module.objects.create(title="Module 1")
        cls.module2 = Module.objects.create(title="Module 2")
        cls.program_module = ProgramModule.objects.create(program=cls.program, module=cls.module1, order=1)
        cls.enrollment = UserProgramEnrollment.objects.create(program=cls.program, user=cls.end_user)

    def test_program_detail_get(self):
        """Test GET request to program detail page."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Program")

    def test_add_modules(self):
        """Test adding a module to a program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        data = {"add_modules": "1", "modules_to_add": [self.module2.id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirects after adding
        self.assertTrue(ProgramModule.objects.filter(program=self.program, module=self.module2).exists())

    def test_duplicate_module_addition(self):
        """Ensure the same module can't be added twice to the same program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        data = {"add_modules": "1", "modules_to_add": [self.module1.id]}
        self.client.post(url, data)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProgramModule.objects.filter(program=self.program, module=self.module1).count(), 1)

    def test_add_users(self):
        """Test adding a user to a program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        new_user = User.objects.create_user(username="newuser", email="newuser@example.com", password="newpassword")
        new_end_user = EndUser.objects.create(user=new_user)
        data = {"add_users": "1", "users_to_add": [new_end_user.user_id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProgramEnrollment.objects.filter(program=self.program, user=new_end_user).exists())

    def test_program_not_found(self):
        """Test attempting to access a non-existent program."""
        url = reverse("program_detail", args=[9999])  # Non-existent program
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_program_delete_nonexistent(self):
        """Test attempting to delete a non-existent program."""
        url = reverse("delete_program", args=[9999])  # Non-existent program
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_program_update_nonexistent(self):
        """Test attempting to update a non-existent program."""
        url = reverse("program_detail", args=[9999])  # Non-existent program
        updated_data = {"title": "Updated Program", "description": "Updated Description"}
        response = self.client.post(url, updated_data)
        self.assertEqual(response.status_code, 404)

    def test_program_module_ordering(self):
        """Test if the modules are ordered correctly in a program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        # Check the order of modules
        data = {"add_modules": "1", "modules_to_add": [self.module2.id]}
        self.client.post(url, data)  # Add second module
        modules = ProgramModule.objects.filter(program=self.program).order_by('order')
        self.assertEqual(modules.first().module, self.module1)
        self.assertEqual(modules.last().module, self.module2)

    # Test for updating program details
    def test_update_program_details(self):
        """Test updating program details."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])  # Change to program_detail
        updated_data = {"title": "Updated Program", "description": "Updated Description", "update_program": "1"}
        response = self.client.post(url, updated_data)
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.program.refresh_from_db()
        self.assertEqual(self.program.title, "Updated Program")
        self.assertEqual(self.program.description, "Updated Description")


    def test_empty_post_data(self):
        """Test submitting an empty POST request (should not change anything)."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)  # No redirect
        self.assertEqual(ProgramModule.objects.filter(program=self.program).count(), 1)
        self.assertEqual(UserProgramEnrollment.objects.filter(program=self.program).count(), 1)


    def test_add_non_existent_module(self):
        """Ensure adding a non-existent module fails."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        invalid_module_id = 9999  # Non-existent module ID
        data = {"add_modules": "1", "modules_to_add": [invalid_module_id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404) 
        self.assertFalse(ProgramModule.objects.filter(program=self.program, module_id=invalid_module_id).exists())

    def test_remove_module_from_program(self):
        """Test removing a module from a program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        data = {"remove_module": self.module1.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect after removing
        self.assertFalse(ProgramModule.objects.filter(program=self.program, module=self.module1).exists())

    def test_enroll_user_to_program(self):
        """Test enrolling a user into a program."""
        self.client.login(username="testuser", password="testpassword")
        new_user = User.objects.create_user(username="newuser", email="newuser@example.com", password="newpassword")
        new_end_user = EndUser.objects.create(user=new_user)
        url = reverse("program_detail", args=[self.program.id])
        data = {"add_users": "1", "users_to_add": [new_end_user.user_id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProgramEnrollment.objects.filter(program=self.program, user=new_end_user).exists())

    def test_remove_user_from_program(self):
        """Test removing a user from a program."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        data = {"remove_user": self.end_user.user_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserProgramEnrollment.objects.filter(program=self.program, user=self.end_user).exists())

    def test_invalid_remove_module(self):
        """Test attempting to remove a non-existent module."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        invalid_module_id = 9999  # Non-existent module
        data = {"remove_module": invalid_module_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Stay on the page, invalid module
        self.assertEqual(ProgramModule.objects.filter(program=self.program).count(), 1)

    def test_user_count_after_enrollment_and_removal(self):
        """Test the user count after enrolling and removing a user."""
        self.client.login(username="testuser", password="testpassword")
        new_user = User.objects.create_user(username="newuser", email="newuser@example.com", password="newpassword")
        new_end_user = EndUser.objects.create(user=new_user)
        
        # Enroll the user
        url = reverse("program_detail", args=[self.program.id])
        data = {"add_users": "1", "users_to_add": [new_end_user.user_id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserProgramEnrollment.objects.filter(program=self.program).count(), 2)

        # Remove the user
        data = {"remove_user": new_end_user.user_id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserProgramEnrollment.objects.filter(program=self.program).count(), 1)

    def test_program_module_ordering(self):
        """Test that the module order is correctly assigned when adding multiple modules."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("program_detail", args=[self.program.id])
        data = {"add_modules": "1", "modules_to_add": [self.module2.id]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Check if the new module was added with correct order
        new_program_module = ProgramModule.objects.get(program=self.program, module=self.module2)
        self.assertEqual(new_program_module.order, 2)


