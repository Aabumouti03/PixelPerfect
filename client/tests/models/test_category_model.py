from django.test import TestCase
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from client.models import Category


class CategoryModelTest(TestCase):
    
    def test_str_representation(self):
        category = Category.objects.create(name="Math")
        self.assertEqual(str(category), "Math")

    def test_category_creation(self):
        category = Category.objects.create(name="Science")
        self.assertTrue(isinstance(category, Category))
        self.assertEqual(category.name, "Science")

    def test_category_name_max_length(self):
        name = "A" * 255  # edge of max_length
        category = Category.objects.create(name=name)
        self.assertEqual(len(category.name), 255)

    def test_create_duplicate_name_if_unique_constraint_exists(self):
        Category.objects.create(name="English")
        # This test assumes name is **not** unique — adjust if it is
        Category.objects.create(name="English")  # Should not fail if not unique

    def test_create_category_blank_name_should_fail(self):
        with self.assertRaises(ValidationError):
            category = Category(name="")
            category.full_clean()  # Enforce field-level validation

    def test_category_querying(self):
        Category.objects.create(name="Physics")
        Category.objects.create(name="Chemistry")
        qs = Category.objects.filter(name__icontains="phy")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "Physics")

    def test_whitespace_handling_in_name(self):
        name = "   Biology   "
        category = Category.objects.create(name=name.strip())
        self.assertEqual(category.name, "Biology")
