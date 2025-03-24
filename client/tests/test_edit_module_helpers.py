from django.test import TestCase
from client.models import Module, Section
from client.editModuleHelpers import get_or_create_general_section 

class GetOrCreateGeneralSectionTest(TestCase):
    def setUp(self):
        self.module = Module.objects.create(title="Algebra")

    def test_creates_new_general_section_if_not_exists(self):
        section = get_or_create_general_section(self.module)
        expected_title = "Algebra - General Exercises"

        self.assertEqual(section.title, expected_title)
        self.assertEqual(section.description, "Auto-generated section for ungrouped exercises.")
        self.assertIn(section, self.module.sections.all())

    def test_returns_existing_section_if_already_exists(self):
        # Create section beforehand
        existing_section = Section.objects.create(
            title="Algebra - General Exercises",
            description="Auto-generated section for ungrouped exercises."
        )
        self.module.sections.add(existing_section)

        section = get_or_create_general_section(self.module)

        self.assertEqual(section, existing_section)
        self.assertEqual(Section.objects.filter(title="Algebra - General Exercises").count(), 1)
