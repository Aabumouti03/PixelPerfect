from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class LogoutViewTestCase(TestCase):
    """Tests for the logout confirmation view restricted to admins."""

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='adminuser', 
            password='password123', 
            email='admin@example.com', 
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser', 
            password='password123',
            email='regular@example.com'
        )

        self.logout_url = reverse('log_out_client')
        self.login_url = reverse('log_in')
        self.dashboard_url = '/client_dashboard/'

    def test_logout_post_request_logs_out_admin_user(self):
        """POST request logs out admin and redirects to login."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.post(self.logout_url)

        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, self.login_url)

    def test_logout_get_request_admin_redirects_dashboard(self):
        """GET request redirects authenticated admin users to dashboard."""
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(self.logout_url)

        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, self.dashboard_url)

    def test_logout_post_request_regular_user_redirects_login(self):
        """Regular user's POST request should redirect to login (no logout)."""
        self.client.login(username='regularuser', password='password123')
        
        response = self.client.post(self.logout_url)

        self.assertIn('_auth_user_id', self.client.session)
        expected_redirect = f"{self.login_url}?next={self.logout_url}"
        
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_logout_get_request_regular_user_redirects_login(self):
        """GET request by regular user redirects to login (permission denied)."""
        self.client.login(username='regularuser', password='password123')
        response = self.client.get(self.logout_url)

        
        expected_redirect = f"{self.login_url}?next={self.logout_url}"
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_logout_post_request_anonymous_redirects_login(self):
        """Anonymous POST request redirects to login page."""
        response = self.client.post(self.logout_url)
        expected_redirect = f"{self.login_url}?next={self.logout_url}"
        
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_logout_get_request_anonymous_user_redirects_login(self):
        """Anonymous GET request redirects to login page."""
        response = self.client.get(self.logout_url)
        expected_redirect = f"{self.login_url}?next={self.logout_url}"
        
        self.assertRedirects(response, expected_redirect, fetch_redirect_response=False)

    def test_logout_get_request_redirects_to_referer(self):
        """Ensure GET request redirects to the referrer URL if available."""
        self.client.login(username='adminuser', password='password123')

        referer_url = self.dashboard_url
        
        response = self.client.get(self.logout_url, HTTP_REFERER=referer_url)

        self.assertRedirects(response, referer_url)
