from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from client.models import Questionnaire, Question, Category
from users.models import EndUser
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class CreateQuestionnaireTest(TestCase):
    """Tests for the create_questionnaire view"""

    def setUp(self):
        """Set up admin and normal user."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="userpass")
        self.end_user = EndUser.objects.create(user=self.normal_user, age=30, gender="female", sector="healthcare")

        # Create test categories
        self.category1 = Category.objects.create(name="Mental Health")
        self.category2 = Category.objects.create(name="Career Development")

        # Login as admin
        self.client.login(username="admin", password="adminpass")
        self.url = reverse("create_questionnaire")

    def test_create_questionnaire_successfully(self):
        """Ensure an admin can create a questionnaire with multiple questions."""
        response = self.client.post(self.url, {
            "title": "Work Readiness Survey",
            "description": "Assessing readiness to return to work",
            "question_text_0": "How confident are you?",
            "question_type_0": "AGREEMENT",
            "sentiment_0": "1",
            "category_0": str(self.category1.id),
            "question_text_1": "How is your mental well-being?",
            "question_type_1": "RATING",
            "sentiment_1": "-1",
            "category_1": str(self.category2.id),
        })

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("manage_questionnaires"))

        # Check if the questionnaire was created
        self.assertTrue(Questionnaire.objects.filter(title="Work Readiness Survey").exists())

        # Check if the questions were created correctly
        questionnaire = Questionnaire.objects.get(title="Work Readiness Survey")
        self.assertEqual(questionnaire.questions.count(), 2)

    def test_missing_title(self):
        """Ensure an error occurs when title is missing."""
        response = self.client.post(self.url, {
            "description": "This is a test",
            "question_text_0": "A test question",
            "question_type_0": "AGREEMENT",
            "sentiment_0": "1",
            "category_0": str(self.category1.id),
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Title is required." in str(m) for m in messages))

    def test_missing_description(self):
        """Ensure an error occurs when description is missing."""
        response = self.client.post(self.url, {
            "title": "Survey without description",
            "question_text_0": "A test question",
            "question_type_0": "AGREEMENT",
            "sentiment_0": "1",
            "category_0": str(self.category1.id),
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Description is required." in str(m) for m in messages))

    def test_create_questionnaire_with_invalid_category(self):
        """Ensure invalid category ID is handled correctly."""
        response = self.client.post(self.url, {
            "title": "Survey With Invalid Category",
            "description": "Testing invalid category handling",
            "question_text_0": "Do you feel supported?",
            "question_type_0": "AGREEMENT",
            "sentiment_0": "1",
            "category_0": "99999",  # Invalid category ID
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Category ID 99999 does not exist." in str(m) for m in messages))

    def test_non_admin_cannot_create_questionnaire(self):
        """Ensure non-admin users cannot access the create questionnaire page."""
        self.client.logout()
        self.client.login(username="user", password="userpass")  # Login as normal user

        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_get_request_renders_template(self):
        """Ensure GET request renders the create questionnaire form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "client/create_questionnaire.html")

    def test_create_questionnaire_with_no_questions(self):
        """Ensure questionnaire cannot be created without at least one question."""
        response = self.client.post(self.url, {
            "title": "Survey Without Questions",
            "description": "A test without questions",
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("At least one question is required." in str(m) for m in messages))

