from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Program  # Adjust the import path as needed

User = get_user_model()

class DeleteProgramTest(TestCase):
    def setUp(self):
        """Set up an admin user and a program to be deleted."""
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="adminpass"
        )
        self.normal_user = User.objects.create_user(
            username="user", email="user@test.com", password="userpass"
        )
        self.client.login(username="admin", password="adminpass")
        
        self.program = Program.objects.create(
            title="Program to Delete",
            description="This program will be deleted in the test."
        )
        
        self.url = reverse("delete_program", args=[self.program.id])

    def test_delete_program_successfully(self):
        """Ensure an admin can delete a program and is redirected."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertFalse(Program.objects.filter(id=self.program.id).exists())

    def test_delete_program_non_admin_user(self):
        """Ensure non-admin users cannot delete a program."""
        self.client.logout()
        self.client.login(username="user", password="userpass")
        response = self.client.get(self.url, follow=True)
        expected_url = reverse("programs") + "?next=" + self.url
        self.assertRedirects(response, expected_url)
        self.assertTrue(Program.objects.filter(id=self.program.id).exists())


    def test_delete_program_not_found(self):
        """Ensure that attempting to delete a non-existent program returns a 404."""
        non_existent_url = reverse("delete_program", args=[999999])
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, 404)
