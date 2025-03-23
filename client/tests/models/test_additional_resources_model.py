import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from client.models import AdditionalResource

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AdditionalResourceModelTest(TestCase):
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_str(self):
        resource = AdditionalResource.objects.create(
            resource_type='book',
            title="Django for Beginners",
            description="A beginner guide to Django"
        )
        expected = "Django for Beginners (book)"
        self.assertEqual(str(resource), expected)

    def test_optional_fields(self):
        resource = AdditionalResource.objects.create(
            resource_type='link',
            title="Official Django Docs"
        )
        self.assertIsNone(resource.description)
        self.assertFalse(resource.file)
        self.assertIsNone(resource.url)

    def test_status_default(self):
        resource = AdditionalResource.objects.create(
            resource_type='podcast',
            title="Django Podcast"
        )
        self.assertEqual(resource.status, "not_started")

    def test_url_field(self):
        url = "https://www.djangoproject.com/"
        resource = AdditionalResource.objects.create(
            resource_type='link',
            title="Django Official",
            url=url
        )
        self.assertEqual(resource.url, url)

    def test_file_upload(self):
        file_content = b"dummy file content"
        file = SimpleUploadedFile("dummy.pdf", file_content, content_type="application/pdf")
        resource = AdditionalResource.objects.create(
            resource_type='pdf',
            title="Django PDF",
            file=file
        )
        self.assertIsNotNone(resource.file.name)
        self.assertTrue(resource.file.name.endswith(".pdf"))

    def test_invalid_resource_type(self):
        resource = AdditionalResource(
            resource_type='invalid',
            title="Invalid Resource"
        )
        with self.assertRaises(ValidationError):
            resource.full_clean()

    def test_update_resource(self):
        resource = AdditionalResource.objects.create(
            resource_type='book',
            title="Django Unchained",
            description="Initial Description"
        )
        resource.description = "Updated Description"
        resource.save()
        resource.refresh_from_db()
        self.assertEqual(resource.description, "Updated Description")

    def test_multiple_resources(self):
        AdditionalResource.objects.create(resource_type='book', title="Book One")
        AdditionalResource.objects.create(resource_type='link', title="Link One")
        AdditionalResource.objects.create(resource_type='survey', title="Survey One")
        self.assertEqual(AdditionalResource.objects.count(), 3)

    def test_description_update(self):
        resource = AdditionalResource.objects.create(
            resource_type='podcast',
            title="Podcast Test",
            description="Initial"
        )
        resource.description = "Updated Podcast Description"
        resource.save()
        resource.refresh_from_db()
        self.assertEqual(resource.description, "Updated Podcast Description")

    def test_str_with_optional_fields(self):
        resource = AdditionalResource.objects.create(
            resource_type='link',
            title="Resource with Extras",
            description="Extra description",
            url="https://example.com"
        )
        expected = "Resource with Extras (link)"
        self.assertEqual(str(resource), expected)
