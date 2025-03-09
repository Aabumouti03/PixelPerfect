from django.test import TestCase
from django.urls import reverse
from django.http import Http404
from client.models import Category, Program, Module

class CategoryDetailViewTests(TestCase):

    def setUp(self):
        # Create a category to test with
        self.category = Category.objects.create(name="Test Category")

        # Create related programs and modules
        self.program1 = Program.objects.create(title="Program 1")
        self.program2 = Program.objects.create(title="Program 2")
        self.module1 = Module.objects.create(title="Module 1")
        self.module2 = Module.objects.create(title="Module 2")
        self.program3 = Program.objects.create(title="Program 3")
        self.program4 = Program.objects.create(title="Program 4")
        self.module3 = Module.objects.create(title="Module 3")
        self.module4 = Module.objects.create(title="Module 4")

        # Assign the category to the programs and modules using set() for many-to-many relationships
        self.program1.categories.set([self.category])
        self.program2.categories.set([self.category])
        self.module1.categories.set([self.category])  # assuming `Module` also uses ManyToManyField
        self.module2.categories.set([self.category])  # assuming `Module` also uses ManyToManyField

        # URL for the category detail view
        self.url = reverse('category_detail', kwargs={'category_id': self.category.id})
        self.invalid_url = reverse('category_detail', kwargs={'category_id': 9999})


    def test_category_detail_view_status_code(self):
        # Test if the page loads with status code 200
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_category_detail_view_template(self):
        # Test if the correct template is used
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'client/category_detail.html')

    def test_category_detail_view_context(self):
        # Test if the correct category, programs, and modules are passed in the context
        response = self.client.get(self.url)
        self.assertEqual(response.context['category'], self.category)
        self.assertEqual(list(response.context['programs']), [self.program1, self.program2])
        self.assertEqual(list(response.context['modules']), [self.module1, self.module2])

    def test_category_detail_view_category_not_found(self):
        # Test if the view returns 404 for a non-existing category
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view_no_programs_or_modules(self):
        # Test when the category has no programs and no modules
        self.category.programs.clear()  # Remove all related programs
        self.category.modules.clear()  # Remove all related modules
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [])
        self.assertEqual(list(response.context['modules']), [])

    def test_category_detail_view_only_programs(self):
        # Test when the category has only programs, no modules
        self.category.modules.clear()  # Remove all related modules
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [self.program1, self.program2])
        self.assertEqual(list(response.context['modules']), [])

    def test_category_detail_view_only_modules(self):
        # Test when the category has only modules, no programs
        self.category.programs.clear()  # Remove all related programs
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['programs']), [])
        self.assertEqual(list(response.context['modules']), [self.module1, self.module2])

    def test_category_detail_view_missing_category_id(self):
        # Test if the URL with a missing category_id raises a 404 error
        response = self.client.get('/category/')
        self.assertEqual(response.status_code, 404)
    
    def test_category_detail_view_invalid_category_id_non_integer(self):
        # Test if passing a non-integer value raises a 404 error
        response = self.client.get('/category/invalid/')
        self.assertEqual(response.status_code, 404)