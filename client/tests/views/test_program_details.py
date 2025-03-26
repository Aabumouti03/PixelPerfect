from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Program, Module, ProgramModule
from users.models import EndUser, UserProgramEnrollment
from django.http import HttpResponseNotFound
from django.db.models import Max

User = get_user_model()

class ProgramDetailViewTest(TestCase):
    """Test suite for the program_detail view"""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        
        cls.admin_user = User.objects.create_superuser(
            username='adminuser', email='adminuser@example.com', password='adminpass'
        )
        cls.admin_profile = EndUser.objects.create(user=cls.admin_user, age=35, gender="male", sector="it")

        cls.regular_user = User.objects.create_user(
            username='regularuser', email='regularuser@example.com', password='regularpass'
        )
        cls.regular_profile = EndUser.objects.create(user=cls.regular_user, age=30, gender="female", sector="healthcare")
        cls.program = Program.objects.create(title="Sample Program", description="Sample Description")
        cls.module1 = Module.objects.create(title="Module 1", description="Module 1 Description")
        cls.module2 = Module.objects.create(title="Module 2", description="Module 2 Description")
        cls.program_module1 = ProgramModule.objects.create(program=cls.program, module=cls.module1, order=1)
        cls.program_module2 = ProgramModule.objects.create(program=cls.program, module=cls.module2, order=2)
        cls.enrollment = UserProgramEnrollment.objects.create(program=cls.program, user=cls.regular_profile)
        cls.url = reverse('program_detail', args=[cls.program.id])

    def test_unauthorized_user_access(self):
        """Test that non-logged in users are redirected to login page"""
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/log_in/?next={self.url}')

    def test_non_admin_user_access(self):
        """Test that non-admin users are not allowed (here we expect a redirect)"""
        self.client.login(username='regularuser', password='regularpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_program_not_found(self):
        """Test for 404 error when the program does not exist"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('program_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_view_program_detail(self):
        """Test that program details are displayed correctly"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertContains(response, "Sample Program")
        self.assertContains(response, "Sample Description")

    def test_empty_program_modules_list(self):
        """Test when a program has no modules"""
        program_no_modules = Program.objects.create(title="Empty Program", description="No modules here.")
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('program_detail', args=[program_no_modules.id]))
        self.assertContains(response, "No modules available")

    def test_remove_module_empty_module_id(self):
        """Test when no module ID is provided for removal"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_module': ''})
        self.assertEqual(response.context.get("error_message"), "No module specified.")

    def test_remove_module_invalid_module_id(self):
        """Test when an invalid module ID is provided for removal"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_module': 'invalid_id'})
        self.assertEqual(response.context.get("error_message"), "Invalid module id.")

    def test_module_not_found_when_removing(self):
        """Test if the module is not found in the program"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_module': 999})
        self.assertEqual(response.context.get("error_message"), "Module not found.")

    def test_successfully_remove_module(self):
        """Test the successful removal of a module from the program"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_module': self.module1.id})
        self.assertRedirects(response, self.url)
        self.assertFalse(ProgramModule.objects.filter(program=self.program, module=self.module1).exists())

    def test_add_modules_empty_module_list(self):
        """Test when no modules are selected for adding"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'add_modules': 'True', 'modules_to_add': []})
        self.assertRedirects(response, self.url)

    def test_add_duplicate_modules(self):
        """Test adding duplicate modules to the program"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url, 
            {'add_modules': 'True', 'modules_to_add': [self.module1.id, self.module1.id]}
        )
        self.assertRedirects(response, f"{self.url}?error_message=Duplicate module added.")

    def test_successfully_add_modules(self):
        """Test adding new modules to the program"""
        new_module = Module.objects.create(title="New Module", description="New Module Description")
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url, 
            {'add_modules': 'True', 'modules_to_add': [new_module.id]}
        )
        self.assertRedirects(response, self.url)
        self.assertTrue(ProgramModule.objects.filter(program=self.program, module=new_module).exists())

    def test_add_users_empty_user_list(self):
        """Test when no users are selected for adding"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'add_users': 'True', 'users_to_add': []})
        self.assertRedirects(response, self.url)

    def test_add_users_successfully(self):
        """Test successfully adding users to the program"""
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='newuserpass')
        new_user_profile = EndUser.objects.create(user=new_user, age=25, gender="male", sector="education")
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url, 
            {'add_users': 'True', 'users_to_add': [new_user.id]}
        )
        self.assertRedirects(response, self.url)
        self.assertTrue(UserProgramEnrollment.objects.filter(program=self.program, user=new_user_profile).exists())
        self.assertEqual(response.status_code, 302)

    def test_remove_user(self):
        """Test the functionality of removing a user from the program"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_user': self.regular_user.id})
        self.assertRedirects(response, self.url)
        self.assertFalse(UserProgramEnrollment.objects.filter(program=self.program, user=self.regular_profile).exists())

    def test_update_program_title(self):
        """Test updating the program title"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'update_program': 'True', 'title': 'Updated Title'})
        self.assertRedirects(response, self.url)
        self.program.refresh_from_db()
        self.assertEqual(self.program.title, 'Updated Title')

    def test_update_program_description(self):
        """Test updating the program description"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'update_program': 'True', 'description': 'Updated Description'})
        self.assertRedirects(response, self.url)
        self.program.refresh_from_db()
        self.assertEqual(self.program.description, 'Updated Description')

    def test_update_program_both_title_and_description(self):
        """Test updating both the program title and description"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(
            self.url, 
            {'update_program': 'True', 'title': 'Updated Title', 'description': 'Updated Description'}
        )
        self.assertRedirects(response, self.url)
        self.program.refresh_from_db()
        self.assertEqual(self.program.title, 'Updated Title')
        self.assertEqual(self.program.description, 'Updated Description')

    def test_redirect_after_adding_modules(self):
        """Test redirect after adding modules"""
        new_module = Module.objects.create(title="New Module", description="New Module Description")
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'add_modules': 'True', 'modules_to_add': [new_module.id]})
        self.assertRedirects(response, self.url)

    def test_redirect_after_removing_users(self):
        """Test redirect after removing a user"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'remove_user': self.regular_user.id})
        self.assertRedirects(response, self.url)

    def test_redirect_after_updating_program(self):
        """Test redirect after updating the program"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'update_program': 'True', 'title': 'Updated Title'})
        self.assertRedirects(response, self.url)

    def test_error_handling_when_adding_invalid_users(self):
        """Test error handling when trying to add a non-existent user"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.post(self.url, {'add_users': 'True', 'users_to_add': [999]})
        self.assertEqual(response.status_code, 404)

    def test_view_all_enrolled_users(self):
        """Test viewing all enrolled users"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertContains(response, self.regular_user.username)

    def test_view_all_modules(self):
        """Test viewing all available modules"""
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)
        self.assertContains(response, self.module1.title)
        self.assertContains(response, self.module2.title)

    def test_empty_enrolled_users_list(self):
        """Test when a program has no enrolled users"""
        program_no_users = Program.objects.create(title="No Users Program", description="No users here.")
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(reverse('program_detail', args=[program_no_users.id]))
        self.assertContains(response, "No users enrolled")
