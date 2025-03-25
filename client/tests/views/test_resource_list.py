import uuid
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.db.models.query import QuerySet
from client.models import AdditionalResource
from unittest.mock import patch

User = get_user_model()

@patch("client.views.admin_check", lambda u: u.is_staff)
class ResourceListViewTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",  
            password="regularpass",
            is_staff=False
        )

        self.url = reverse("resource_list")

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_non_admin_user_redirected(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_admin_user_access(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "client/resource_list.html")

    def test_context_contains_resources(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertIn("resources", response.context)

    def test_context_resources_is_queryset(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["resources"], QuerySet)

    def test_no_resources(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["resources"].count(), 0)

    def test_one_resource(self):
        self.client.force_login(self.admin_user)
        AdditionalResource.objects.create(resource_type="book", title="Django for Beginners")
        response = self.client.get(self.url)
        self.assertEqual(response.context["resources"].count(), 1)

    def test_multiple_resources(self):
        self.client.force_login(self.admin_user)
        AdditionalResource.objects.create(resource_type="book", title="Book One")
        AdditionalResource.objects.create(resource_type="link", title="Link One")
        response = self.client.get(self.url)
        self.assertEqual(response.context["resources"].count(), 2)

    def test_reverse_url_resolution(self):
        url = reverse("resource_list")
        self.assertTrue(url)

    def test_anonymous_redirect_includes_next(self):
        response = self.client.get(self.url)
        self.assertIn("next=", response.url)

    def test_admin_access_after_logout_fails(self):
        self.client.force_login(self.admin_user)
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_view_renders_correct_content(self):
        self.client.force_login(self.admin_user)
        AdditionalResource.objects.create(
            resource_type="link", title="Official Django Docs", url="https://www.djangoproject.com/"
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Official Django Docs")

    def test_post_request_behaves_like_get(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)

    def test_updated_resource_reflected(self):
        self.client.force_login(self.admin_user)
        resource = AdditionalResource.objects.create(resource_type="book", title="Old Title")
        resource.title = "New Title"
        resource.save()
        response = self.client.get(self.url)
        self.assertContains(response, "New Title")
