from django.test import TestCase
from django.contrib.auth import get_user_model
from client.models import Module, Category, BackgroundStyle, ModuleRating
from users.models import User, EndUser


class ModuleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="testt1@example.com", password="testpass")
        self.enduser = EndUser.objects.create(user=self.user)
        self.category = Category.objects.create(name="Technology")
        self.bg_style = BackgroundStyle.objects.create(
            background_color="#ffffff",
            background_image="pattern1"
        )
        self.module = Module.objects.create(
            title="Intro to AI",
            description="Basics of Artificial Intelligence",
            background_style=self.bg_style
        )
        self.module.categories.add(self.category)

    def test_str_representation(self):
        self.assertEqual(str(self.module), "Intro to AI")

    def test_average_rating_no_ratings(self):
        self.assertEqual(self.module.average_rating(), 0)

    def test_average_rating_with_ratings(self):
        user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpass")
        user3 = User.objects.create_user(username="testuser3", email="test3@example.com", password="testpass")
        enduser2 = EndUser.objects.create(user=user2)
        enduser3 = EndUser.objects.create(user=user3)

        ModuleRating.objects.create(module=self.module, user=self.enduser, rating=4)
        ModuleRating.objects.create(module=self.module, user=enduser2, rating=5)
        ModuleRating.objects.create(module=self.module, user=enduser3, rating=3)

        self.assertEqual(self.module.average_rating(), 4.0)
