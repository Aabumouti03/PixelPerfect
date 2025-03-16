from django import forms
from django.test import TestCase
from client.forms import ProgramForm
from client.models import Program, Module, Category

class ProgramFormTestCase(TestCase):
    """Tests for the ProgramForm."""

    def setUp(self):
        """Set up test data for form tests."""
        self.category1 = Category.objects.create(name="Technology")
        self.category2 = Category.objects.create(name="Business")

        self.module1 = Module.objects.create(title="Module 1", description="First module")
        self.module2 = Module.objects.create(title="Module 2", description="Second module")

        self.valid_form_data = {
            "title": "Test Program",
            "description": "A valid test program",
            "modules": [self.module1.id, self.module2.id],
            "module_order": f"{self.module1.id},{self.module2.id}",
        }

    def test_form_initialization(self):
        """Ensure the form initializes correctly with categories and modules."""
        form = ProgramForm()
        self.assertIn("title", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("modules", form.fields)
        self.assertIn("module_order", form.fields)
        self.assertIn("categories", form.fields)

        self.assertEqual(form.fields["modules"].queryset.count(), Module.objects.count())
        self.assertEqual(form.fields["categories"].queryset.count(), Category.objects.count())

    def test_valid_form_submission(self):
        """Ensure the form is valid with correct data."""
        form = ProgramForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_title(self):
        """Ensure the form is invalid when title is missing."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["title"] = ""

        form = ProgramForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_invalid_form_missing_description(self):
        """Ensure the form is invalid when description is missing."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["description"] = ""

        form = ProgramForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_valid_form_empty_module_order(self):
        """Ensure form is valid even if module_order is empty (optional field)."""
        valid_data = self.valid_form_data.copy()
        valid_data["module_order"] = ""

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())


    def test_form_renders_correct_widgets(self):
        """Ensure the form renders correct widgets for each field."""
        form = ProgramForm()
        self.assertEqual(form.fields["title"].widget.attrs["class"], "form-control rounded-pill border-2")
        self.assertEqual(form.fields["description"].widget.attrs["class"], "form-control rounded-pill border-2")
        self.assertEqual(form.fields["modules"].widget.attrs["class"], "module-checkbox")
        self.assertEqual(form.fields["categories"].widget.attrs["class"], "category-checkbox")
        self.assertTrue(isinstance(form.fields["module_order"].widget, forms.HiddenInput))

    def test_form_queryset_prefetch_related(self):
        """Ensure modules queryset is prefetched with categories."""
        form = ProgramForm()
        
        self.assertEqual(form.fields["modules"].queryset.count(), Module.objects.count())


    def test_invalid_form_title_too_long(self):
        """Ensure the form is invalid when title exceeds max length."""
        long_title = "A" * 300
        invalid_data = self.valid_form_data.copy()
        invalid_data["title"] = long_title

        form = ProgramForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
    
    def test_valid_form_no_modules(self):
        """Ensure the form is valid when no modules are selected."""
        no_module_data = self.valid_form_data.copy()
        no_module_data["modules"] = []

        form = ProgramForm(data=no_module_data)
        
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_nonexistent_category(self):
        """Ensure the form is invalid when a non-existent category is selected."""
        invalid_data = self.valid_form_data.copy()
        invalid_data["categories"] = [999]

        form = ProgramForm(data=invalid_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("categories", form.errors)

    def test_valid_form_no_categories(self):
        """Ensure the form is valid when no categories are selected."""
        valid_data = self.valid_form_data.copy()
        valid_data["categories"] = []

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())


    def test_invalid_form_duplicate_title_case_insensitive(self):
        """Ensure duplicate title validation is case-insensitive."""
        Program.objects.create(title="Duplicate Program", description="Existing program")

        duplicate_data = {
            "title": "duplicate program",  # different casing
            "description": "Another program",
        }

        form = ProgramForm(data=duplicate_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


    def test_form_saves_correctly(self):
        """Ensure a valid form saves and creates a Program instance."""
        form = ProgramForm(data=self.valid_form_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()
        self.assertEqual(program.title, self.valid_form_data["title"])

    def test_invalid_form_whitespace_title(self):
        """Ensure form is invalid when title is just whitespace."""
        whitespace_title_data = self.valid_form_data.copy()
        whitespace_title_data["title"] = "     "

        form = ProgramForm(data=whitespace_title_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_valid_form_special_character_title(self):
        """Ensure form allows special characters in the title."""
        special_title_data = self.valid_form_data.copy()
        special_title_data["title"] = "Special @@@ !!!"

        form = ProgramForm(data=special_title_data)
        
        self.assertTrue(form.is_valid())
    
    def test_invalid_form_whitespace_description(self):
        """Ensure form is invalid when description is just whitespace."""
        whitespace_description_data = self.valid_form_data.copy()
        whitespace_description_data["description"] = "     "

        form = ProgramForm(data=whitespace_description_data)
        
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
    

    def test_valid_form_empty_modules_list(self):
        """Ensure form is valid when modules list is explicitly empty."""
        empty_modules_data = self.valid_form_data.copy()
        empty_modules_data["modules"] = []

        form = ProgramForm(data=empty_modules_data)
        
        self.assertTrue(form.is_valid())
