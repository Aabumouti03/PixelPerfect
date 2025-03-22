from django.test import TestCase
from django.urls import reverse

class StaticPageTests(TestCase):
    def test_welcome_page(self):
        response = self.client.get(reverse('welcome_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/welcome_page.html')

    def test_about_page(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/about.html')

    def test_contact_us_page(self):
        response = self.client.get(reverse('contact_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/contact_us.html')
