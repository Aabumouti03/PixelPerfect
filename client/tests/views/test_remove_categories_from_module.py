from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Module, Category
import json

User = get_user_model()

class RemoveCategoriesFromModuleTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create admin user and login
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpass'
        )
        self.client.login(username='admin', password='adminpass')

        # Create module and categories
        self.module = Module.objects.create(title="Test Module", description="Description")
        self.cat1 = Category.objects.create(name="Python")
        self.cat2 = Category.objects.create(name="Django")
        self.module.categories.add(self.cat1, self.cat2)

        self.url = reverse("remove_categories_from_module", args=[self.module.id])

    def test_remove_single_category(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_ids': [self.cat1.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn({'id': self.cat1.id, 'name': self.cat1.name}, response.json()['removed_categories'])
        self.assertNotIn(self.cat1, self.module.categories.all())

    def test_remove_multiple_categories(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_ids': [self.cat1.id, self.cat2.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['removed_categories']), 2)
        self.assertFalse(self.module.categories.exists())

    def test_remove_nonexistent_category(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_ids': [999]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['removed_categories'], [])
        self.assertTrue(self.module.categories.exists())  # Original categories still present

    def test_remove_with_empty_list(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'category_ids': []}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['removed_categories'], [])

    def test_remove_with_missing_category_ids_key(self):
        response = self.client.post(
            self.url,
            data=json.dumps({}),  # no category_ids key
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['removed_categories'], [])

    def test_invalid_json_payload(self):
        response = self.client.post(
            self.url,
            data="not a json",
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
