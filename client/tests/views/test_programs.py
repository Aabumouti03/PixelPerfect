from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Program, Module, ProgramModule
from users.models import Admin

User = get_user_model()

class ProgramsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('programs')

        # Create admin user and link to Admin profile
        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            password='adminpass',
            first_name='Admin',
            last_name='User',
            email='admin@example.com'
        )
        Admin.objects.create(user=self.admin_user)

        # Create normal user (no Admin profile)
        self.normal_user = User.objects.create_user(
            username='normaluser',
            password='userpass',
            first_name='Normal',
            last_name='User',
            email='user@example.com'
        )

        # Sample program and modules
        self.module1 = Module.objects.create(title='Module 1', description='Desc 1')
        self.program = Program.objects.create(title='Program 1', description='Desc 1')
        ProgramModule.objects.create(program=self.program, module=self.module1, order=1)

    def test_admin_user_can_access_programs(self):
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/programs.html')
        self.assertIn('programs', response.context)
        self.assertEqual(len(response.context['programs']), 1)

    def test_normal_user_redirected(self):
        self.client.login(username='normaluser', password='userpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/log_in/'))

    def test_admin_access_with_no_programs(self):
        Program.objects.all().delete()
        self.client.login(username='adminuser', password='adminpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/programs.html')
        self.assertEqual(len(response.context['programs']), 0)

