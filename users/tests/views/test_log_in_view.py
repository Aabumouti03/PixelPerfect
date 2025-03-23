from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth import login, logout
from users.forms import LogInForm

User = get_user_model()

class LogInViewTestCase(TestCase):
    """Unit Tests for the login view"""

    def setUp(self):
        """Set up test user and login URL"""
        self.url = reverse('log_in')
        self.dashboard_url = reverse('dashboard')


        self.test_user = User.objects.create_user(username='dandoe', password='Testuser123')

    def test_log_in_url(self):
        """Ensure the login URL resolves correctly."""
        self.assertEqual(self.url, '/log_in/')

    def test_get_log_in_page(self):
        """Test that the login page loads correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/log_in.html')
        form = response.context['form']
        self.assertIsInstance(form, LogInForm)
        self.assertFalse(form.is_bound)

    def test_successful_log_in_redirects_to_dashboard(self):
        """Test that a user logs in successfully and gets redirected to the dashboard."""
        self.test_user.email_verified = True
        self.test_user.save()

        form_input = {'username': 'dandoe', 'password': 'Testuser123'}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, self.dashboard_url)

        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_unsuccessful_log_in_shows_errors(self):
        """Test that incorrect credentials result in an error message."""
        form_input = {'username': 'dandoe', 'password': 'WrongPassword'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/log_in.html')

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('__all__', form.errors)

    def test_login_with_non_existent_user_fails(self):
        """Test that login fails when user does not exist."""
        form_input = {'username': 'unknownuser', 'password': 'SomePass123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/log_in.html')

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('__all__', form.errors)

    def test_login_with_empty_form_fails(self):
        """Test that submitting an empty form does not authenticate."""
        form_input = {'username': '', 'password': ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

    def test_redirect_if_not_authenticated(self):
        """Ensure an unauthenticated user is redirected to login when accessing the dashboard."""
        response = self.client.get(self.dashboard_url, follow=True)
        self.assertRedirects(response, f"{self.url}?next={self.dashboard_url}")


    def test_successful_logout(self):
        """Ensure a logged-in user can log out and is redirected to login."""
        self.client.login(username='dandoe', password='Testuser123')

        response = self.client.get(reverse('log_out'), follow=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('log_out'), follow=True)
        self.assertRedirects(response, reverse('log_in'))

        response = self.client.get(reverse('dashboard'), follow=True)
        self.assertRedirects(response, f"{reverse('log_in')}?next={reverse('dashboard')}")

    def test_cancel_logout_stays_on_page(self):
        """Ensure user stays on the same page if they cancel logout."""
        self.client.login(username='dandoe', password='Testuser123')

        response = self.client.get(reverse('log_out'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/dashboard.html')
    
    def test_logout_without_being_logged_in(self):
        """Ensure unauthenticated users cannot log out (should be redirected to login)."""
        response = self.client.post(reverse('log_out'), follow=True)

        final_redirect = response.redirect_chain[-1][0] if response.redirect_chain else response.request['PATH_INFO']

        self.assertTrue(final_redirect.startswith(reverse('log_in')))

    
    def test_login_trims_spaces_and_succeeds(self):
        """Ensure authentication succeeds even if username/password have leading/trailing spaces."""
        self.test_user.email_verified = True
        self.test_user.save()

        form_input = {'username': '  dandoe  ', 'password': '  Testuser123  '}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, self.dashboard_url)

        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_admin_login_redirects_to_client_dashboard(self):
        """Ensure superusers log in and are redirected to the client dashboard."""
        admin_user = User.objects.create_superuser(
            username="adminuser", email="admin@example.com", password="AdminPass123"
        )
        admin_user.email_verified = True
        admin_user.save()

        form_input = {'username': 'adminuser', 'password': 'AdminPass123'}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, reverse('client_dashboard'))

    def test_login_fails_for_unverified_email(self):
        """Ensure users with unverified emails cannot log in."""
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',  # Ensure unique email
            password='Test1234!'
        )
        unverified_user.email_verified = False
        unverified_user.save()

        form_input = {'username': 'unverified', 'password': 'Test1234!'}
        response = self.client.post(self.url, form_input)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/log_in.html")
        self.assertContains(response, "You must verify your email before logging in.")


    def test_login_redirects_to_next_url(self):
        """Ensure users are redirected to their original destination after logging in."""
        protected_url = reverse("dashboard")  # Replace with an actual protected page
        login_url_with_next = f"{self.url}?next={protected_url}"

        self.test_user.email_verified = True
        self.test_user.save()

        form_input = {'username': 'dandoe', 'password': 'Testuser123'}
        response = self.client.post(login_url_with_next, form_input, follow=True)

        self.assertRedirects(response, protected_url)


    def test_case_insensitive_login_view(self):
        """Ensure the login view handles username case insensitivity correctly."""
        self.test_user.email_verified = True
        self.test_user.save()

        form_input = {'username': 'DANdoe', 'password': 'Testuser123'}
        response = self.client.post(self.url, form_input, follow=True)

        self.assertRedirects(response, self.dashboard_url)

        user = authenticate(username='dandoe', password='Testuser123')
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)