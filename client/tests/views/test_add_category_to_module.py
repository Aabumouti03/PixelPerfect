from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, Category
import json

User = get_user_model()

class AddCategoryToModuleTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        # Create a module and a category
        self.module = Module.objects.create(title="Test Module", description="Description")
        self.category = Category.objects.create(name="Python")

        # URL assuming your view is registered like: path('modules/<int:module_id>/add_category/', ...)
        self.url = reverse('add_category_to_module', args=[self.module.id])

    def test_add_valid_category_to_module(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_id': self.category.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['category_name'], self.category.name)
        self.assertIn(self.category, self.module.categories.all())

    def test_add_nonexistent_category(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_id': 999}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['status'], 'error')
        self.assertEqual(response.json()['message'], 'Category not found')

    def test_invalid_json_payload(self):
        response = self.client.post(
            self.url,
            data="not a json",
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)  # JSONDecodeError will be raised

    def test_missing_category_id(self):
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)  # category_id=None → .get(id=None) → DoesNotExist
