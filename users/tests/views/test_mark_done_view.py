from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from client.models import Module, Exercise, AdditionalResource, Section
from users.models import EndUser, UserModuleProgress
import json
from users.models import User 


class MarkDoneViewTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create a Module
        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        # Create exercises and add them to a Section
        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank", status="in_progress")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice", status="completed")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        # Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book", status="in_progress")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf", status="completed")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # Create EndUser
        self.end_user = EndUser.objects.create(user=self.user)

        # Log the user in
        self.client.login(username='testuser', password='testpassword')

    def test_mark_resource_done(self):
        # The URL for marking a resource as done
        url = reverse('mark_done')

        # Prepare the data for marking a resource as completed
        data = {
            "id": self.resource_1.id,
            "type": "resource",
            "action": "done"
        }

        # Perform the POST request
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 50})  # Update with the expected progress value

        # Reload the resource from the database
        self.resource_1.refresh_from_db()

        # Assert the resource status is now 'completed'
        self.assertEqual(self.resource_1.status, 'completed')

    def test_mark_exercise_done(self):
        # The URL for marking an exercise as done
        url = reverse('mark_done')

        # Prepare the data for marking an exercise as completed
        data = {
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "done"
        }

        # Perform the POST request
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 75})  # Update with the expected progress value

        # Reload the exercise from the database
        self.exercise_1.refresh_from_db()

        # Assert the exercise status is now 'completed'
        self.assertEqual(self.exercise_1.status, 'completed')

    def test_mark_undo_resource(self):
        # The URL for marking a resource as undone
        url = reverse('mark_done')

        # Prepare the data for undoing the resource completion
        data = {
            "id": self.resource_1.id,
            "type": "resource",
            "action": "undo"
        }

        # Perform the POST request
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 25})  # Update with the expected progress value

        # Reload the resource from the database
        self.resource_1.refresh_from_db()

        # Assert the resource status is now 'in_progress'
        self.assertEqual(self.resource_1.status, 'in_progress')

    def test_mark_undo_exercise(self):
        # The URL for marking an exercise as undone
        url = reverse('mark_done')

        # Prepare the data for undoing the exercise completion
        data = {
            "id": self.exercise_2.id,
            "type": "exercise",
            "action": "undo"
        }

        # Perform the POST request
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 50})  # Update with the expected progress value

        # Reload the exercise from the database
        self.exercise_2.refresh_from_db()

        # Assert the exercise status is now 'in_progress'
        self.assertEqual(self.exercise_2.status, 'in_progress')

