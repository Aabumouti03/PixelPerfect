"""Unit Tests of the log out view"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='dandoe', password='Testuser123'
        )
        self.client.login(username='dandoe', password='Testuser123')
        self.logout_url = reverse('log_out')
        self.login_url = reverse('log_in')
        self.dashboard_url = reverse('dashboard')
    
    def test_logout_post_request(self):
        """Test that a POST request logs out the user and redirects to login page."""
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_logout_get_request_redirects_back(self):
        """Test that a GET request redirects back to the referer if provided."""
        referer_url = self.dashboard_url
        response = self.client.get(self.logout_url, HTTP_REFERER=referer_url)
        self.assertRedirects(response, referer_url)
    
    def test_logout_get_request_redirects_to_dashboard_if_no_referer(self):
        """Test that a GET request redirects to the dashboard if no referer is set."""
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.dashboard_url)

    def test_anonymous_user_logout_attempt(self):
        """Test that an anonymous user trying to log out does not cause an error."""
        self.client.logout()
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, self.login_url)

    def test_get_request_does_not_log_out_user(self):
        """Test that a GET request does not log out the user."""
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.dashboard_url)
        self.assertIn('_auth_user_id', self.client.session)
