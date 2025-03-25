import uuid
from django.urls import reverse
from django.http import Http404
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from client.models import AdditionalResource
from unittest.mock import patch

User = get_user_model()

@patch("client.views.admin_check", lambda user: user.is_staff)
class DeleteResourceViewTest(TestCase):
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

        self.resource = AdditionalResource.objects.create(
            resource_type="book",
            title="Django for Beginners"
        )
        self.list_url = reverse("resource_list")
        self.delete_url = reverse("delete_resource", kwargs={"resource_id": self.resource.id})

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_non_admin_user_redirected(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_admin_user_get_redirects_without_deletion(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())

    def test_admin_user_post_deletes_resource(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)
        with self.assertRaises(AdditionalResource.DoesNotExist):
            AdditionalResource.objects.get(id=self.resource.id)

    def test_invalid_resource_id_returns_404(self):
        self.client.force_login(self.admin_user)
        invalid_url = reverse("delete_resource", kwargs={"resource_id": 99999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 404)


    def test_get_request_does_not_delete_resource(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())

    def test_redirect_url_after_deletion(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, self.list_url)

    def test_delete_only_removes_target_resource(self):
        self.client.force_login(self.admin_user)
        resource2 = AdditionalResource.objects.create(resource_type="link", title="Link Resource")
        delete_url_resource2 = reverse("delete_resource", kwargs={"resource_id": resource2.id})
        response = self.client.post(delete_url_resource2)
        self.assertRedirects(response, self.list_url)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())
        with self.assertRaises(AdditionalResource.DoesNotExist):
            AdditionalResource.objects.get(id=resource2.id)

    def test_admin_access_before_post_no_deletion(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())

    def test_non_admin_post_does_not_delete_resource(self):
        self.client.force_login(self.regular_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())

    def test_delete_resource_with_valid_id(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(AdditionalResource.DoesNotExist):
            AdditionalResource.objects.get(id=self.resource.id)

    def test_multiple_resources_deletion(self):
        self.client.force_login(self.admin_user)
        resource2 = AdditionalResource.objects.create(resource_type="pdf", title="PDF Resource")
        resource3 = AdditionalResource.objects.create(resource_type="survey", title="Survey Resource")
        delete_url_resource2 = reverse("delete_resource", kwargs={"resource_id": resource2.id})
        self.client.post(delete_url_resource2)
        self.assertTrue(AdditionalResource.objects.filter(id=self.resource.id).exists())
        self.assertTrue(AdditionalResource.objects.filter(id=resource3.id).exists())
        self.assertFalse(AdditionalResource.objects.filter(id=resource2.id).exists())

    def test_response_status_for_methods(self):
        self.client.force_login(self.admin_user)
        response_get = self.client.get(self.delete_url)
        self.assertEqual(response_get.status_code, 302)
        response_post = self.client.post(self.delete_url)
        self.assertEqual(response_post.status_code, 302)

    def test_admin_access_after_logout_fails(self):
        self.client.force_login(self.admin_user)
        self.client.logout()
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/log_in/", response.url)

    def test_unsupported_method_redirects(self):
        self.client.force_login(self.admin_user)
        response = self.client.put(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.list_url)
