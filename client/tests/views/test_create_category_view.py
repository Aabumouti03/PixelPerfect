from django.test import TestCase
from django.urls import reverse
from client.models import Category, Module, Program
from client.forms import CategoryForm

class CreateCategoryViewTests(TestCase):

    def setUp(self):
        # Create some modules and programs to test with
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.program1 = Program.objects.create(title="Program 1")
        self.program2 = Program.objects.create(title="Program 2")

        # URL for the category creation view
        self.url = reverse('create_category')

    def test_create_category_get(self):
        # Test that the view renders the form correctly on GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/create_category.html')
        self.assertIsInstance(response.context['form'], CategoryForm)

    def test_create_category_post_valid(self):
        # Test POST with valid data
        data = {
            'name': 'New Category',
            'modules': [self.module1.id, self.module2.id],
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created
        category = Category.objects.get(name='New Category')
        self.assertEqual(category.modules.count(), 2)  # Modules should be set
        self.assertEqual(category.programs.count(), 2)  # Programs should be set

    def test_create_category_post_no_modules_or_programs(self):
        # Test POST with no modules or programs selected
        data = {
            'name': 'New Category No Modules or Programs',
            'modules': [],
            'programs': [],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created without any modules or programs
        category = Category.objects.get(name='New Category No Modules or Programs')
        self.assertEqual(category.modules.count(), 0)  # No modules should be set
        self.assertEqual(category.programs.count(), 0)  # No programs should be set

    def test_create_category_post_only_one_module(self):
        # Test POST with only one module selected
        data = {
            'name': 'Category with One Module',
            'modules': [self.module1.id],
            'programs': [self.program1.id, self.program2.id],  # Multiple programs
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created with the correct associations
        category = Category.objects.get(name='Category with One Module')
        self.assertEqual(category.modules.count(), 1)  # One module should be set
        self.assertEqual(category.programs.count(), 2)  # Two programs should be set

    def test_create_category_post_only_one_program(self):
        # Test POST with only one program selected
        data = {
            'name': 'Category with One Program',
            'modules': [self.module1.id, self.module2.id],  # Multiple modules
            'programs': [self.program1.id],  # Only one program
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertRedirects(response, reverse('category_list'))

        # Check if the category was created with the correct associations
        category = Category.objects.get(name='Category with One Program')
        self.assertEqual(category.modules.count(), 2)  # Two modules should be set
        self.assertEqual(category.programs.count(), 1)  # One program should be set

    def test_create_category_post_invalid(self):
        # Test POST with invalid data (e.g., missing required fields)
        data = {
            'name': '',  # Invalid because 'name' is required
            'modules': [],
            'programs': [],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed

        # Access the form from response.context and check for errors
        form = response.context['form']
        self.assertTrue(form.errors)  # Check that errors exist

    def test_create_category_post_no_data(self):
        # Test POST with no data submitted
        data = {}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed

        # Access the form from response.context and check for errors
        form = response.context['form']
        self.assertTrue(form.errors)  # Check that errors exist

    def test_create_category_post_invalid_modules_ids(self):
        # Test POST with invalid modules' ids
        data = {
            'name': 'Invalid Category',
            'modules': [999],  # Non-existent module ID
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed
        form = response.context['form']
        self.assertTrue(form.errors)  # Check for errors

    def test_create_category_post_invalid_programs_ids(self):
        # Test POST with invalid programs' ids
        data = {
            'name': 'Invalid Programs Category',
            'modules': [self.module1.id, self.module2.id],
            'programs': [999],  # Non-existent program ID
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed
        form = response.context['form']
        self.assertTrue(form.errors)  # Check for errors

    def test_create_category_post_blank_name(self):
        # Test POST with a blank name
        data = {
            'name': '',  # Blank name should trigger an error
            'modules': [self.module1.id, self.module2.id],
            'programs': [self.program1.id, self.program2.id],
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)  # The form should be redisplayed
