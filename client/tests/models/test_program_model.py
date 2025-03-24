from django.test import TestCase
from client.models import Program, Category, Module, ProgramModule

class ProgramModelTest(TestCase):
    
    def setUp(self):
        self.category1 = Category.objects.create(name="Math")
        self.category2 = Category.objects.create(name="Science")
        
        self.module1 = Module.objects.create(title="Algebra")
        self.module2 = Module.objects.create(title="Biology")

        self.program = Program.objects.create(
            title="STEM Basics",
            description="A foundational STEM program."
        )
        self.program.categories.add(self.category1, self.category2)
        ProgramModule.objects.create(program=self.program, module=self.module1, order=1)
        ProgramModule.objects.create(program=self.program, module=self.module2, order=2)


    def test_str_representation(self):
        self.assertEqual(str(self.program), "STEM Basics")

    def test_program_has_categories(self):
        categories = self.program.categories.all()
        self.assertIn(self.category1, categories)
        self.assertIn(self.category2, categories)
        self.assertEqual(categories.count(), 2)

    def test_program_has_modules_through_relationship(self):
        modules = self.program.modules.all()
        self.assertIn(self.module1, modules)
        self.assertIn(self.module2, modules)
        self.assertEqual(modules.count(), 2)
