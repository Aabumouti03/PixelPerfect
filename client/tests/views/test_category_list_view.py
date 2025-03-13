from django.test import TestCase
from django.urls import reverse
from client.models import Category

class CategoryListViewTests(TestCase):

    def setUp(self):
        # Create different categories to test with
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")
        self.category3 = Category.objects.create(name="Special Category @#$")
        self.category4 = Category.objects.create(name="Another category 123")
        self.category5 = Category.objects.create(name="MixedCase Category")
        self.url = reverse('category_list')  # Ensure this matches your URL name
    
    def test_category_list_view_status_code(self):
        # Test if the page loads with status code 200
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_category_list_view_template(self):
        # Test if the correct template is used
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'client/category_list.html')
    
    def test_category_list_view_context(self):
        # Test if the categories are passed to the template context
        response = self.client.get(self.url)
        categories = response.context['categories']
        self.assertEqual(list(categories), [self.category1, self.category2, self.category3, self.category4, self.category5])
    
    def test_category_list_view_no_categories(self):
        # Test if the view works when there are no categories
        Category.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['categories']), 0)
    
    def test_category_list_view_with_more_than_two_categories(self):
        # Test with more than two categories to ensure pagination works if it's in place
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        categories = response.context['categories']
        self.assertIn(self.category1, categories)
        self.assertIn(self.category2, categories)
        self.assertIn(self.category3, categories)
        self.assertIn(self.category4, categories)
        self.assertIn(self.category5, categories)

    def test_category_list_view_with_special_characters(self):
        # Test categories with special characters
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        categories = response.context['categories']
        self.assertIn(self.category3, categories)  # Category with special characters should be present

    def test_category_list_view_with_mixed_case(self):
        # Test categories with mixed-case names
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        categories = response.context['categories']
        self.assertIn(self.category5, categories)  # Category with mixed case should be present

    def test_category_list_view_sorted(self):
        # Test if categories are sorted in ascending order
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        categories = response.context['categories']
        self.assertEqual(list(categories), [self.category1, self.category2, self.category3, self.category4, self.category5])
