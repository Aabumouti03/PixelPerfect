from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import EndUser
from client.models import Module, ModuleRating
import json

User = get_user_model()

class RateModuleTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@example.com"
        )
        
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpassword",
            email="testuser2@example.com"
        )

        self.module = Module.objects.create(title="Test Module", description="Test Module Description")
        self.client = Client()

    def test_authenticated_user_can_rate_module(self):
        """Test that an authenticated user can successfully submit a rating."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})
        response = self.client.post(url, json.dumps({"rating": 4}), content_type="application/json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["average_rating"], 4.0)
        self.assertEqual(data["user_rating"], 4)
        self.assertIn("message", data)
        self.assertEqual(ModuleRating.objects.count(), 1)

    def test_rating_updates_when_user_rates_again(self):
        """Test that a user's rating updates when they submit a new rating."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})

        # First rating
        self.client.post(url, json.dumps({"rating": 3}), content_type="application/json")

        # Update the rating
        response = self.client.post(url, json.dumps({"rating": 5}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["user_rating"], 5)
        self.assertEqual(ModuleRating.objects.count(), 1)
        self.assertEqual(ModuleRating.objects.first().rating, 5)

    def test_average_rating_calculation(self):
        """Test that average rating is correctly calculated with multiple users."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})
        self.client.post(url, json.dumps({"rating": 5}), content_type="application/json")

        self.client.logout()
        self.client.login(username="testuser2", password="testpassword")
        self.client.post(url, json.dumps({"rating": 3}), content_type="application/json")

        self.assertEqual(ModuleRating.objects.count(), 2)
        ratings = ModuleRating.objects.filter(module=self.module).values_list("rating", flat=True)
        expected_avg = round(sum(ratings) / len(ratings), 1)
        self.assertEqual(expected_avg, 4.0)

    def test_invalid_rating_rejected(self):
        """Test that invalid ratings (out of range) are rejected."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})

        response = self.client.post(url, json.dumps({"rating": 7}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "Invalid rating. Must be between 1 and 5."}
        )

        response = self.client.post(url, json.dumps({"rating": -2}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "Invalid rating. Must be between 1 and 5."}
        )

    def test_non_integer_rating_rejected(self):
        """Test that non-integer ratings are rejected."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})

        response = self.client.post(url, json.dumps({"rating": "bad_value"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "Invalid rating format."}
        )

    def test_invalid_json_data(self):
        """Test that invalid JSON data does not crash the view."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})
        response = self.client.post(url, "invalid-json", content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "Invalid JSON data."}
        )

    def test_unauthenticated_user_cannot_rate(self):
        """Test that unauthenticated users cannot rate a module."""
        url = reverse("rate_module", kwargs={"module_id": self.module.id})
        response = self.client.post(url, json.dumps({"rating": 4}), content_type="application/json")
        self.assertEqual(response.status_code, 302) 

    def test_get_request_is_rejected(self):
        """Test that a GET request is rejected."""
        self.client.login(username="testuser", password="testpassword")
        url = reverse("rate_module", kwargs={"module_id": self.module.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": False, "message": "Invalid request method."}
        )
