from django.test import TestCase
from client.forms import ModuleForm
from client.models import Module

class ModuleFormTest(TestCase):
    def test_valid_form(self):
        """
        Test that the form is valid with proper data.
        """
        data = {
            'title': 'Unique Title',
            'description': 'A nice description'
        }
        form = ModuleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_blank_title(self):
        """
        Test that the form is invalid if title is blank.
        """
        data = {
            'title': '',
            'description': 'Description without a title'
        }
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        # The form should have an error on the 'title' field
        self.assertIn('title', form.errors)

    def test_duplicate_title(self):
        """
        Test that the form is invalid if the title (case-insensitive) already exists.
        """
        # Create a module with a certain title
        Module.objects.create(title='DuplicateTitle', description='Some description')

        # Attempt to create another module with the same title in different case
        data = {
            'title': 'duplicatetitle',
            'description': 'Another description'
        }
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        # The form should have an error on the 'title' field
        self.assertIn('title', form.errors)
        self.assertEqual(
            form.errors['title'],
            ['A module with this title already exists.']
        )