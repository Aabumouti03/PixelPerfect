from django.test import TestCase
from client.models import Program, Module, Category, ProgramModule


class ProgramModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech")
        self.module = Module.objects.create(title="Intro to Python")
        self.module2 = Module.objects.create(title="Advanced Python")
        self.program = Program.objects.create(
            title="Beginner Programming",
            description="A program for beginners."
        )
        self.program.categories.add(self.category)
        self.program_module = ProgramModule.objects.create(
            program=self.program,
            module=self.module,
            order=1
        )
        self.program_module2 = ProgramModule.objects.create(
            program=self.program,
            module=self.module2,
            order=2
        )

    def test_program_module_str_representation(self):
        expected_str = "Beginner Programming - Intro to Python (Order: 1)"
        self.assertEqual(str(self.program_module), expected_str)

    def test_program_str_representation(self):
        self.assertEqual(str(self.program), "Beginner Programming")

    def test_program_has_categories(self):
        self.assertEqual(self.program.categories.count(), 1)
        self.assertIn(self.category, self.program.categories.all())

    def test_program_has_modules_through_relationship(self):
        modules = self.program.modules.all()
        self.assertEqual(modules.count(), 2)
        self.assertIn(self.module, modules)
        self.assertIn(self.module2, modules)

    def test_programmodule_ordering(self):
        program_modules = ProgramModule.objects.filter(program=self.program)
        self.assertEqual(list(program_modules), [self.program_module, self.program_module2])

    def test_duplicate_order_in_same_program_should_fail(self):
        with self.assertRaises(Exception):
            ProgramModule.objects.create(
                program=self.program,
                module=Module.objects.create(title="Extra Module"),
                order=1  # Duplicate order
            )

    def test_same_order_allowed_in_different_programs(self):
        program2 = Program.objects.create(title="Intermediate Programming")
        # Same order, but different program — should be OK
        try:
            ProgramModule.objects.create(program=program2, module=self.module, order=1)
        except Exception:
            self.fail("ProgramModule with same order in different program should be allowed")
