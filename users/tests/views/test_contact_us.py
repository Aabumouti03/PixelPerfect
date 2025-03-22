from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch

class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_us_get(self):
        """
        Test that a GET request to the contact_us view returns the contact_us.html template.
        """
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact_us.html')

    @patch('users.views.send_mail')
    def test_contact_us_post(self, mock_send_mail):
        """
        Test that a POST request to the contact_us view:
          - Constructs the full_message correctly.
          - Calls send_mail with the correct parameters.
          - Redirects to the contact_success view.
        """
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'message': 'This is a test message.'
        }
        response = self.client.post(reverse('contact_us'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('contact_success'))

        expected_message = (
            f"Name: {data['name']}\n"
            f"Email: {data['email']}\n\n"
            f"Message:\n{data['message']}"
        )
        mock_send_mail.assert_called_once_with(
            subject="New Contact Us Submission",
            message=expected_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

    @patch('users.views.send_mail')
    def test_contact_us_post_missing_email(self, mock_send_mail):
        """
        Test that a POST request missing the 'email' field still calls send_mail,
        with 'None' substituted for the missing email.
        """
        data = {
            'name': 'Test User',
            # 'email' is intentionally missing
            'message': 'Message without email.'
        }
        response = self.client.post(reverse('contact_us'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('contact_success'))

        expected_message = (
            f"Name: {data['name']}\n"
            f"Email: {None}\n\n"
            f"Message:\n{data['message']}"
        )
        mock_send_mail.assert_called_once_with(
            subject="New Contact Us Submission",
            message=expected_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

    @patch('users.views.send_mail', side_effect=Exception("Test exception"))
    def test_contact_us_post_send_mail_exception(self, mock_send_mail):
        """
        Test that if send_mail raises an exception, the view propagates it.
        """
        data = {
            'name': 'Test User',
            'email': 'testuser@example.com',
            'message': 'This is a test message.'
        }
        with self.assertRaises(Exception) as context:
            self.client.post(reverse('contact_us'), data)
        self.assertIn("Test exception", str(context.exception))

    def test_contact_success_get(self):
        """
        Test that a GET request to the contact_success view returns the correct template.
        """
        response = self.client.get(reverse('contact_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact_success.html')

    def test_contact_success_post(self):
        """
        Test that a POST request to the contact_success view (even if unexpected)
        still returns the correct template.
        """
        response = self.client.post(reverse('contact_success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact_success.html')
