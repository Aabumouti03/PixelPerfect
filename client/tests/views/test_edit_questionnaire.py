from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from client.models import Questionnaire, Question, Category
from users.models import EndUser

User = get_user_model()

class EditQuestionnaireTest(TestCase):
    """Tests for the edit_questionnaire view."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(username="admin", email="admin@test.com", password="adminpass")
        self.normal_user = User.objects.create_user(username="user", email="user@test.com", password="userpass")

        self.category1 = Category.objects.create(name="Mental Health")
        self.category2 = Category.objects.create(name="Career Growth")

        self.questionnaire = Questionnaire.objects.create(
            title="Work Readiness Survey",
            description="Assessing readiness to return to work",
            is_active=True
        )

        self.question1 = Question.objects.create(
            questionnaire=self.questionnaire,
            question_text="How confident are you?",
            question_type="AGREEMENT",
            sentiment=1,
            category=self.category1
        )

        self.client.login(username="admin", password="adminpass")
        self.url = reverse("edit_questionnaire", args=[self.questionnaire.id])

    def test_edit_questionnaire_successfully(self):
        """Ensure an admin can edit a questionnaire successfully."""
        response = self.client.post(self.url, {
            "title": "Updated Survey",
            "description": "Updated description",
            f"question_text_{self.question1.id}": "Updated Question",
            f"question_type_{self.question1.id}": "RATING",
            f"sentiment_{self.question1.id}": "-1",
            f"category_{self.question1.id}": str(self.category2.id),
        })

        self.assertEqual(response.status_code, 302) 

        self.questionnaire.refresh_from_db()
        self.question1.refresh_from_db()

        self.assertEqual(self.questionnaire.title, "Updated Survey")
        self.assertEqual(self.questionnaire.description, "Updated description")
        self.assertEqual(self.question1.question_text, "Updated Question")
        self.assertEqual(self.question1.question_type, "RATING")
        self.assertEqual(self.question1.sentiment, -1)
        self.assertEqual(self.question1.category, self.category2)

    def test_edit_questionnaire_with_empty_title(self):
        """Ensure an empty title is not allowed."""
        response = self.client.post(self.url, {"title": "", "description": "Valid description"}, follow=True)
        self.assertContains(response, "Title is required.") 
        self.questionnaire.refresh_from_db()
        self.assertNotEqual(self.questionnaire.title, "")

    def test_edit_questionnaire_with_empty_description(self):
        """Ensure an empty description is not allowed."""
        response = self.client.post(self.url, {"title": "Valid Title", "description": ""}, follow=True)
        self.assertContains(response, "Description is required.") 
        self.questionnaire.refresh_from_db()
        self.assertNotEqual(self.questionnaire.description, "")

    def test_edit_questionnaire_with_invalid_category(self):
        """Ensure an invalid category ID is handled properly."""
        response = self.client.post(self.url, {
            "title": "Valid Title",
            "description": "Valid description",
            f"question_text_{self.question1.id}": "Valid Question",
            f"category_{self.question1.id}": "9999",  # Invalid category ID
        }, follow=True)

        self.assertContains(response, "Invalid category ID 9999.")

    def test_edit_questionnaire_with_invalid_sentiment(self):
        """Ensure an invalid sentiment value is handled properly."""
        response = self.client.post(self.url, {
            "title": "Valid Title",
            "description": "Valid description",
            f"sentiment_{self.question1.id}": "invalid",  # Invalid sentiment
        }, follow=True)

        self.assertContains(response, f"Invalid sentiment value for question {self.question1.id}.")

    def test_non_admin_cannot_edit_questionnaire(self):
        """Ensure non-admin users cannot access the edit page."""
        self.client.logout()
        self.client.login(username="user", password="userpass")  # Normal user

        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, f"{reverse('log_in')}?next={self.url}")

    def test_edit_questionnaire_without_questions(self):
        """Ensure a questionnaire cannot be edited if no questions exist."""
        self.question1.delete()  # Remove all questions
        response = self.client.post(self.url, {"title": "Valid Title", "description": "Valid description"}, follow=True)

        self.assertContains(response, "At least one question is required.")  
