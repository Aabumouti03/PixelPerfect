from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import Module, Category, BackgroundStyle, ModuleRating
from users.models import User, EndUser


class ModuleRatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
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
        rating = ModuleRating.objects.create(module=self.module, user=self.enduser, rating=5)
        expected = f"{self.enduser.user.username} rated {self.module.title} - 5/5"
        self.assertEqual(str(rating), expected)

    def test_rating_within_valid_range(self):
        rating = ModuleRating(module=self.module, user=self.enduser, rating=3)
        # should not raise any validation error
        try:
            rating.full_clean()
        except ValidationError:
            self.fail("ModuleRating raised ValidationError unexpectedly!")

    def test_rating_below_min_value(self):
        rating = ModuleRating(module=self.module, user=self.enduser, rating=0)
        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_rating_above_max_value(self):
        rating = ModuleRating(module=self.module, user=self.enduser, rating=6)
        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_rating_above_max_value(self):
        rating = ModuleRating(module=self.module, user=self.enduser, rating=10)
        with self.assertRaises(ValidationError):
            rating.full_clean()

    def test_unique_user_module_rating(self):
        ModuleRating.objects.create(module=self.module, user=self.enduser, rating=4)
        duplicate = ModuleRating(module=self.module, user=self.enduser, rating=5)
        with self.assertRaises(Exception):
            duplicate.save()
