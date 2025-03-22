from django.test import TestCase, Client
from django.urls import reverse
from users.models import EndUser, UserModuleEnrollment
from client.models import Module
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class EnrollmentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        self.module = Module.objects.create(title="Module 1", description="Description 1")
        self.end_user = EndUser.objects.create(user=self.user)

        self.enroll_url = reverse('enroll_module')
        self.unenroll_url = reverse('unenroll_module')

    ## Test successful enrollment
    def test_enroll_module_success(self):
        data = {"title": "Module 1"}
        response = self.client.post(self.enroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), True)
        self.assertTrue(UserModuleEnrollment.objects.filter(user=self.end_user, module=self.module).exists())

    ## Test enrollment fails for non-existent module
    def test_enroll_module_not_found(self):
        data = {"title": "Non-existent Module"}
        response = self.client.post(self.enroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get("error"), "Module not found")

    ##  Test enrollment fails if already enrolled
    def test_enroll_module_already_enrolled(self):
        UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)
        data = {"title": "Module 1"}
        response = self.client.post(self.enroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Already enrolled")

    ## Test enrollment fails with invalid data
    def test_enroll_module_invalid_request(self):
        data = {"wrong_field": "Module 1"}
        response = self.client.post(self.enroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Missing module title")

    ## Test successful unenrollment
    def test_unenroll_module_success(self):
        UserModuleEnrollment.objects.create(user=self.end_user, module=self.module)
        data = {"title": "Module 1"}
        response = self.client.post(self.unenroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(UserModuleEnrollment.objects.filter(user=self.end_user, module=self.module).exists())

    ## Test unenrollment fails if not enrolled
    def test_unenroll_module_not_enrolled(self):
        data = {"title": "Module 1"}
        response = self.client.post(self.unenroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Not enrolled")

    ## Test unenrollment fails for non-existent module
    def test_unenroll_module_not_found(self):
        data = {"title": "Non-existent Module"}
        response = self.client.post(self.unenroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get("error"), "Module not found")

    ## Test unenrollment fails with invalid request
    def test_unenroll_module_invalid_request(self):
        data = {"wrong_field": "Module 1"}
        response = self.client.post(self.unenroll_url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Missing module title")
        
    def test_unenroll_module_user_not_found(self):
        # Delete the EndUser object
        EndUser.objects.all().delete()

        data = {"title": "Module 1"}
        response = self.client.post(self.unenroll_url, json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "User not found")
        
    def test_enroll_module_invalid_json(self):
        # Send broken JSON
        data = '{"title": "Module 1"'
        response = self.client.post(self.enroll_url, data, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Invalid JSON")
        
        
    def test_unenroll_module_invalid_json(self):
        data = '{"title": "Module 1"'  # Broken JSON
        response = self.client.post(self.unenroll_url, data, content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Invalid JSON")
        
    def test_enroll_module_invalid_request_method(self):
        response = self.client.get(self.enroll_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Invalid request")
        
    def test_unenroll_module_invalid_request_method(self):
        response = self.client.get(self.unenroll_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("error"), "Invalid request")