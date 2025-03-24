from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Category, Module, Program
from client.forms import CategoryForm

User = get_user_model()

class EditCategoryTestCase(TestCase):

    def setUp(self):
        
        """Set up initial test data."""
        self.client = Client()


        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            password="adminpassword",
            email="admin@example.com"
        )

    
        self.regular_user = User.objects.create_user(
            username="regularuser",
            password="userpassword",
            email="user@example.com"
        )

    
        self.category = Category.objects.create(name="Test Category")


        self.module1 = Module.objects.create(title="Module 1", description="First module")
        self.module2 = Module.objects.create(title="Module 2", description="Second module")

        self.program1 = Program.objects.create(title="Program 1", description="First program")
        self.program2 = Program.objects.create(title="Program 2", description="Second program")

        self.edit_url = reverse("edit_category", kwargs={"category_id": self.category.id})


    def test_admin_can_access_edit_page(self):
        """Test if admin can access the edit category page."""
        self.client.login(username="adminuser", password="adminpassword")
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Category")


    def test_non_admin_cannot_access_edit_page(self):
        """Test that a non-admin user is blocked from accessing edit category."""
        self.client.login(username="regularuser", password="userpassword")
        response = self.client.get(self.edit_url)
        self.assertNotEqual(response.status_code, 200)  


    def test_edit_category_updates_successfully(self):
        """Test if submitting the edit form updates the category."""
        self.client.login(username="adminuser", password="adminpassword")

        post_data = {
            "name": "Updated Category",
            "modules": [self.module1.id, self.module2.id],
            "programs": [self.program1.id, self.program2.id]
        }

        response = self.client.post(self.edit_url, post_data, follow=True)
        self.category.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.category.name, "Updated Category")
        self.assertEqual(list(self.category.modules.all()), [self.module1, self.module2])
        self.assertEqual(list(self.category.programs.all()), [self.program1, self.program2])


    def test_invalid_form_submission(self):
        """Test that invalid form data does not update the category."""
        self.client.login(username="adminuser", password="adminpassword")

        invalid_data = {
            "name": "",  
        }

        response = self.client.post(self.edit_url, invalid_data)

        self.category.refresh_from_db()

        self.assertNotEqual(self.category.name, "") 
        self.assertEqual(response.status_code, 200)


        self.assertTrue(response.context["form"].errors)
        self.assertIn("name", response.context["form"].errors)  
