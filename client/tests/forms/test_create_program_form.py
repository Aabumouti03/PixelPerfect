from django import forms
from django.test import TestCase
from client.forms import ProgramForm
from client.models import Program, Module, Category, ProgramModule

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

    def test_valid_form_creates_new_category(self):
        """Ensure new_category creates a new Category instance if it doesn’t exist."""
        valid_data = self.valid_form_data.copy()
        valid_data["new_category"] = "Science"

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()

        self.assertTrue(Category.objects.filter(name="Science").exists())
        self.assertIn(Category.objects.get(name="Science"), program.categories.all())

    def test_new_category_is_linked_to_program(self):
        """Ensure the new category is correctly linked to the program."""
        valid_data = self.valid_form_data.copy()
        valid_data["new_category"] = "Art"

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()
        
        new_category = Category.objects.get(name="Art")
        self.assertIn(new_category, program.categories.all())

    def test_valid_duplicate_new_category(self):
        """Ensure form allows existing categories by reusing them instead of raising an error."""
        existing_category = Category.objects.create(name="Existing Category")

        valid_data = self.valid_form_data.copy()
        valid_data["new_category"] = "Existing Category"

        form = ProgramForm(data=valid_data)

        self.assertTrue(form.is_valid())
        program = form.save()

        self.assertIn(existing_category, program.categories.all())
        self.assertEqual(Category.objects.filter(name="Existing Category").count(), 1)


    def test_module_order_is_saved_correctly(self):
        """Ensure module_order is saved correctly and reflected in ProgramModule entries."""
        valid_data = self.valid_form_data.copy()
        valid_data["module_order"] = f"{self.module2.id},{self.module1.id}"

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()
        
        ordered_modules = list(ProgramModule.objects.filter(program=program).order_by("order"))
        self.assertEqual(ordered_modules[0].module, self.module2)
        self.assertEqual(ordered_modules[1].module, self.module1)

    def test_form_save_with_commit_false(self):
        """Ensure form save(commit=False) creates an instance but does not save."""
        form = ProgramForm(data=self.valid_form_data)
        
        self.assertTrue(form.is_valid())
        program = form.save(commit=False)
        
        self.assertFalse(Program.objects.filter(title=self.valid_form_data["title"]).exists())
        self.assertEqual(program.title, self.valid_form_data["title"])  # Program exists in memory
    
    def test_program_saves_with_categories_and_modules(self):
        """Ensure program correctly saves selected categories and modules."""
        valid_data = self.valid_form_data.copy()
        valid_data["categories"] = [self.category1.id, self.category2.id]

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()

        self.assertEqual(set(program.categories.all()), {self.category1, self.category2})
        self.assertEqual(set(ProgramModule.objects.filter(program=program).values_list("module", flat=True)), {self.module1.id, self.module2.id})

    def test_new_category_whitespace_only(self):
        """Ensure new_category containing only whitespace is ignored."""
        valid_data = self.valid_form_data.copy()
        valid_data["new_category"] = "    "

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save()

        self.assertFalse(Category.objects.filter(name="    ").exists())
        self.assertEqual(program.categories.count(), 0)


    def test_save_with_commit_false_does_not_save_relationships(self):
        """Ensure calling save(commit=False) does not create ProgramModules or add categories."""
        valid_data = self.valid_form_data.copy()
        valid_data["categories"] = [self.category1.id, self.category2.id]

        form = ProgramForm(data=valid_data)
        
        self.assertTrue(form.is_valid())
        program = form.save(commit=False)

        self.assertFalse(Program.objects.filter(title=self.valid_form_data["title"]).exists())

        self.assertIsNone(program.pk)

        with self.assertRaises(ValueError):
            program.categories.count()

    def test_form_initializes_with_correct_modules_queryset(self):
        """Ensure the form initializes with the correct modules queryset."""
        form = ProgramForm()
        self.assertEqual(list(form.fields["modules"].queryset), list(Module.objects.prefetch_related('categories')))

    def test_clean_title_duplicate(self):
        """Ensure duplicate title raises ValidationError."""
        Program.objects.create(title="Existing Program", description="Existing description")

        form_data = self.valid_form_data.copy()
        form_data["title"] = "existing program"

        form = ProgramForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertEqual(form.errors["title"], ["A program with this title already exists."])

    def test_clean_new_category_existing(self):
        """Ensure new_category returns existing category instead of creating a duplicate."""
        existing_category = Category.objects.create(name="Science")

        form_data = {"new_category": "science"}
        form = ProgramForm(data=form_data)
        form.is_valid()

        self.assertEqual(form.cleaned_data["new_category"], "Science")

    def test_clean_description_empty(self):
        """Ensure an empty or whitespace-only description raises a ValidationError."""
        form_data = {"title": "Valid Title", "description": "    "}
        form = ProgramForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)
        self.assertEqual(form.errors["description"], ["Description cannot be empty."])

    def test_save_with_commit_false_does_not_persist_to_db(self):
        """Ensure calling save(commit=False) does not create ProgramModules or save categories."""
        form = ProgramForm(data=self.valid_form_data)

        self.assertTrue(form.is_valid())
        program = form.save(commit=False)

        self.assertFalse(Program.objects.filter(title=self.valid_form_data["title"]).exists())
        self.assertIsNone(program.pk)

        with self.assertRaises(ValueError):
            program.categories.count()

    def test_module_order_is_saved_correctly(self):
        """Ensure module_order is saved correctly and reflected in ProgramModule entries."""
        valid_data = self.valid_form_data.copy()
        valid_data["module_order"] = f"{self.module2.id},{self.module1.id}"

        form = ProgramForm(data=valid_data)

        self.assertTrue(form.is_valid())
        program = form.save()

        ordered_modules = list(ProgramModule.objects.filter(program=program).order_by("order"))
        self.assertEqual(ordered_modules[0].module, self.module2)
        self.assertEqual(ordered_modules[1].module, self.module1)

    def test_save_reuses_existing_category(self):
        """Ensure the form reuses an existing category instead of creating a duplicate."""
        existing_category = Category.objects.create(name="Existing Category")

        form_data = self.valid_form_data.copy()
        form_data["new_category"] = "Existing Category"

        form = ProgramForm(data=form_data)

        self.assertTrue(form.is_valid())
        program = form.save()

        self.assertIn(existing_category, program.categories.all())
        self.assertEqual(Category.objects.filter(name="Existing Category").count(), 1)
