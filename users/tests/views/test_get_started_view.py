from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser
from client.models import Category, Program, Module

User = get_user_model()

class GetStartedViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.end_user = EndUser.objects.create(user=self.user, age=25, gender='female', sector='it', last_time_to_work='1_month')
        self.category1 = Category.objects.create(name="Health")
        self.category2 = Category.objects.create(name="Tech")
        self.program1 = Program.objects.create(title="Program A", description="Desc A")
        self.program1.categories.add(self.category1)
        self.module1 = Module.objects.create(title="Module A", description="Desc A")
        self.module1.categories.add(self.category1)
        self.url = reverse("get_started")

    def login(self):
        self.client.login(username="testuser", password="password123")

    def test_initial_load_returns_all_programs_modules(self):
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.program1, response.context["programs"])
        self.assertIn(self.module1, response.context["modules"])

    def test_search_filters_programs_and_modules(self):
        self.login()
        response = self.client.get(self.url, {"search": "Program A", "search_btn": "1"})
        self.assertContains(response, "Program A")
        self.assertNotContains(response, "Module A")

    def test_filter_type_programs_only(self):
        self.login()
        response = self.client.get(self.url, {"filter": "1", "filter_type": "programs", "category": [str(self.category1.id)]})
        self.assertIn(self.program1, response.context["programs"])
        self.assertEqual(list(response.context["modules"]), [])

    def test_filter_type_modules_only(self):
        self.login()
        response = self.client.get(self.url, {"filter": "1", "filter_type": "modules", "category": [str(self.category1.id)]})
        self.assertIn(self.module1, response.context["modules"])
        self.assertEqual(list(response.context["programs"]), [])

    def test_sorting_ascending(self):
        Program.objects.create(title="Program Z", description="Z Desc")
        self.login()
        response = self.client.get(self.url, {"sort": "asc"})
        program_titles = [p.title for p in response.context["programs"]]
        self.assertEqual(program_titles, sorted(program_titles))

    def test_sorting_descending(self):
        Program.objects.create(title="Program Z", description="Z Desc")
        self.login()
        response = self.client.get(self.url, {"sort": "desc"})
        program_titles = [p.title for p in response.context["programs"]]
        self.assertEqual(program_titles, sorted(program_titles, reverse=True))

    def test_all_categories_selected_logic(self):
        self.login()
        response = self.client.get(self.url, {
            "filter": "1",
            "filter_type": "all",
            "category": [str(self.category1.id), str(self.category2.id)]
        })
        self.assertIn(self.program1, response.context["programs"])

    def test_no_categories_defined(self):
        Category.objects.all().delete()
        self.login()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


    def test_search_resets_filters(self):
        self.login()
        response = self.client.get(self.url, {
            "search": "Program A",
            "search_btn": "1",
            "filter_type": "modules",
            "category": [str(self.category1.id)]
        })
        self.assertEqual(response.context["filter_type"], "all")
        self.assertIn(self.program1, response.context["programs"])

    def test_search_yields_no_results(self):
        self.login()
        response = self.client.get(self.url, {"search": "Nonexistent", "search_btn": "1"})
        self.assertEqual(list(response.context["programs"]), [])
        self.assertEqual(list(response.context["modules"]), [])

