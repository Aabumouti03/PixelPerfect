from django.test import TestCase
from django.core.exceptions import ValidationError
from client.models import BackgroundStyle, BACKGROUND_IMAGE_CHOICES


class BackgroundStyleModelTest(TestCase):
    def test_str_representation(self):
        bg_style = BackgroundStyle.objects.create(
            background_color='#ffcc00',
            background_image='pattern2'
        )
        expected_str = "Background Style: #ffcc00 - pattern2"
        self.assertEqual(str(bg_style), expected_str)

    def test_get_background_image_url_returns_correct_url(self):
        expected_url = dict(BACKGROUND_IMAGE_CHOICES)['pattern2']
        style = BackgroundStyle.objects.create(
            background_color="#ffffff",
            background_image="pattern2"
        )
        self.assertEqual(style.get_background_image_url(), expected_url)

    def test_get_background_image_url_returns_none_for_invalid_choice(self):
        style = BackgroundStyle.objects.create(
            background_color="#ffffff",
            background_image="unknown_pattern"
        )
        self.assertIsNone(style.get_background_image_url())

    def test_default_background_color(self):
        style = BackgroundStyle.objects.create(background_image="pattern1")
        self.assertEqual(style.background_color, '#73c4fd')

    def test_default_background_image(self):
        style = BackgroundStyle.objects.create(background_color="#abcdef")
        self.assertEqual(style.background_image, 'pattern1')

    def test_all_background_image_choices_are_accepted(self):
        for key, _ in BACKGROUND_IMAGE_CHOICES:
            style = BackgroundStyle.objects.create(
                background_color="#ffffff",
                background_image=key
            )
            self.assertEqual(style.background_image, key)

    def test_background_color_allows_hex_edge_cases(self):
        style = BackgroundStyle(
            background_color="#000000",
            background_image="pattern1"
        )
        style.full_clean()

    def test_background_image_required(self):
        style = BackgroundStyle(background_color="#ffffff", background_image=None)
        with self.assertRaises(ValidationError):
            style.full_clean()
