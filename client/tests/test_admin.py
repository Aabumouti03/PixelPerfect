from django.test import TestCase
from django.contrib.admin.sites import site
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import (
    Program, Module, Section, Exercise, AdditionalResource, Category, ProgramModule, 
    BackgroundStyle, ModuleRating, Questionnaire, Question, VideoResource, ExerciseQuestion
)
from client.admin import ProgramAdmin, ModuleAdmin, SectionAdmin, ExerciseAdmin, AdditionalResourceAdmin, ExerciseQuestionAdmin
from users.models import EndUser, User

class AdminSiteTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Create an admin user for testing."""
        User = get_user_model()
        cls.admin_user = User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")

    def setUp(self):
        """Log in the admin user before each test."""
        self.client.login(username="admin", password="adminpass")

    ### 🔹 1️⃣ Test Model Registration in Admin ###
    def test_models_registered_in_admin(self):
        """Ensure all models are registered in the Django admin site."""
        models = [Program, Module, Section, Exercise, AdditionalResource, Category, ProgramModule, 
                  BackgroundStyle, ModuleRating, Questionnaire, Question, VideoResource]
        
        for model in models:
            with self.subTest(model=model.__name__):
                self.assertIn(model, site._registry)

    ### 🔹 2️⃣ Test Admin Configurations ###
    def test_admin_list_display(self):
        """Ensure list_display fields are correctly configured."""
        self.assertEqual(ProgramAdmin.list_display, ('title', 'description', 'display_categories'))
        self.assertEqual(ModuleAdmin.list_display, ('title', 'description', 'average_rating', 'display_categories'))
        self.assertEqual(SectionAdmin.list_display, ('title', 'diagram_preview', 'text_position_from_diagram'))
        self.assertEqual(ExerciseAdmin.list_display, ('title', 'exercise_type', 'question_count', 'status'))

    def test_admin_search_fields(self):
        """Ensure search_fields are correctly set."""
        self.assertEqual(ProgramAdmin.search_fields, ('title', 'description'))
        self.assertEqual(ModuleAdmin.search_fields, ('title', 'description'))
        self.assertEqual(SectionAdmin.search_fields, ('title', 'description'))
        self.assertEqual(ExerciseAdmin.search_fields, ('title',))

    ### 🔹 3️⃣ Test Admin Panel Access ###
    def test_admin_login_required(self):
        """Test that the admin page requires authentication."""
        self.client.logout()
        response = self.client.get(reverse("admin:index"))
        self.assertRedirects(response, "/admin/login/?next=/admin/")

    def test_admin_page_loads(self):
        """Ensure the admin page for models loads correctly."""
        response = self.client.get(reverse("admin:client_program_changelist"))
        self.assertEqual(response.status_code, 200)

    ### 🔹 4️⃣ Test Custom Admin Methods ###
    def test_display_categories_direct(self):
        """Ensure display_categories() method correctly formats category names."""
        
        # Create test program and categories
        program = Program.objects.create(title="Test Program")
        category1 = Category.objects.create(name="Math")
        category2 = Category.objects.create(name="Science")
        program.categories.add(category1, category2)  

        # Refresh from DB to ensure category relationships are loaded
        program.refresh_from_db()

        # Get the admin instance
        admin_instance = ProgramAdmin(Program, site)

        # Directly call the display_categories method
        result = admin_instance.display_categories(program)
        
        # Check if the result is formatted correctly
        self.assertEqual(result, "Math, Science")
    
    def test_display_categories_in_admin(self):
        """Ensure display_categories() method is executed in the Django Admin panel."""

        User = get_user_model()

        # Ensure an admin user exists
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "password": "adminpass", "is_superuser": True, "is_staff": True}
        )

        self.client.login(username="admin", password="adminpass")

        # Create a test program with categories
        program = Program.objects.create(title="Test Program")
        category1 = Category.objects.create(name="Math")
        category2 = Category.objects.create(name="Science")
        program.categories.add(category1, category2)

        # Access the admin change list page
        response = self.client.get(reverse("admin:client_program_changelist"))

        # Ensure the page loads successfully
        self.assertEqual(response.status_code, 200)

        # Check if the category names appear in the response content
        self.assertContains(response, "Math, Science")


    
    def test_average_rating(self):
        """Ensure average_rating() method works correctly."""
        
        # Create test users
        User = get_user_model()
        user1 = User.objects.create(username="user1", email="user1@example.com", password="testpass")
        user2 = User.objects.create(username="user2", email="user2@example.com", password="testpass")

        enduser1 = EndUser.objects.create(user=user1)
        enduser2 = EndUser.objects.create(user=user2)

        # Create test module
        module = Module.objects.create(title="Test Module", description="Test Description")

        # Assign ratings using different users
        ModuleRating.objects.create(module=module, user=enduser1, rating=4)
        ModuleRating.objects.create(module=module, user=enduser2, rating=5)

        # Get admin instance and check average rating calculation
        admin_instance = ModuleAdmin(Module, site)
        result = admin_instance.average_rating(module)
        
        self.assertEqual(result, 4.5)  # (4+5)/2 = 4.5


    def test_diagram_preview(self):
        """Ensure diagram_preview() method correctly displays status."""
        section_with_diagram = Section.objects.create(title="With Diagram", diagram="test.png")
        section_without_diagram = Section.objects.create(title="Without Diagram")

        admin_instance = SectionAdmin(Section, site)
        self.assertEqual(admin_instance.diagram_preview(section_with_diagram), "✅ Diagram Uploaded")
        self.assertEqual(admin_instance.diagram_preview(section_without_diagram), "❌ No Diagram")

    def test_file_or_url(self):
        """Ensure file_or_url() method works correctly."""
        resource_with_file = AdditionalResource.objects.create(title="File Resource", file="test.pdf")
        resource_with_url = AdditionalResource.objects.create(title="URL Resource", url="http://example.com")
        resource_empty = AdditionalResource.objects.create(title="Empty Resource")

        admin_instance = AdditionalResourceAdmin(AdditionalResource, site)
        self.assertEqual(admin_instance.file_or_url(resource_with_file), "📄 File Uploaded")
        self.assertEqual(admin_instance.file_or_url(resource_with_url), "🔗 URL Provided")
        self.assertEqual(admin_instance.file_or_url(resource_empty), "❌ No Resource")
    
    def test_question_count(self):
        """Ensure question_count() method returns the correct number of questions."""
        exercise = Exercise.objects.create(title="Test Exercise", exercise_type="MCQ")
        question1 = ExerciseQuestion.objects.create(question_text="Q1")
        question2 = ExerciseQuestion.objects.create(question_text="Q2")
        exercise.questions.add(question1, question2)  # Add questions

        admin_instance = ExerciseAdmin(Exercise, site)
        result = admin_instance.question_count(exercise)
        self.assertEqual(result, 2)  # Expecting 2 questions

    def test_question_preview(self):
        """Ensure question_preview() method correctly formats questions."""
        question_with_blank = ExerciseQuestion.objects.create(
            question_text="Fill in the blank",
            has_blank=True,
            text_before_blank="The capital of France is",
            text_after_blank="."
        )
        question_without_blank = ExerciseQuestion.objects.create(
            question_text="What is 2+2?",
            has_blank=False
        )

        admin_instance = ExerciseQuestionAdmin(ExerciseQuestion, site)
        result_with_blank = admin_instance.question_preview(question_with_blank)
        result_without_blank = admin_instance.question_preview(question_without_blank)

        self.assertEqual(result_with_blank, "The capital of France is ____ .")  # Expected blank format
        self.assertEqual(result_without_blank, "What is 2+2?")  # Expected normal question



