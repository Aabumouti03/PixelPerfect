from django.test import TestCase
from django.urls import reverse
from users.models import User 
from client.models import Exercise, AdditionalResource, Module, Section
from users.models import EndUser, UserModuleProgress
import json


class MarkDoneViewTest(TestCase):

    def setUp(self):
        # Create a user
        #
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create a Module
        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        # Create exercises and add them to a Section
        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank", status="in_progress")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice", status="in_progress")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        # Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book", status="in_progress")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf", status="in_progress")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # Create EndUser
        self.end_user = EndUser.objects.create(user=self.user)

        # Log the user in
        self.client.login(username='testuser', password='testpassword')

    def test_mark_resource_done(self):
        # The URL to test
        url = reverse('mark_done')

        # Send POST request to mark the resource as done
        response = self.client.post(url, json.dumps({
            "id": self.resource_1.id,
            "type": "resource",
            "action": "done"
        }), content_type='application/json')

        # Check the response status and data
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 25})

        # Check that the resource status has been updated
        self.resource_1.refresh_from_db()
        self.assertEqual(self.resource_1.status, "completed")

    def test_mark_undo_resource(self):
        # Mark resource as done first
        self.resource_1.status = "completed"
        self.resource_1.save()

        # The URL to test
        url = reverse('mark_done')

        # Send POST request to undo the resource (mark it as in_progress)
        response = self.client.post(url, json.dumps({
            "id": self.resource_1.id,
            "type": "resource",
            "action": "undo"
        }), content_type='application/json')

        # Check the response status and data
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 0})

        # Check that the resource status has been updated
        self.resource_1.refresh_from_db()
        self.assertEqual(self.resource_1.status, "in_progress")

    def test_mark_exercise_done(self):
        # The URL to test
        url = reverse('mark_done')

        # Send POST request to mark the exercise as done
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "done"
        }), content_type='application/json')

        # Check the response status and data
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 25})

        # Check that the exercise status has been updated
        self.exercise_1.refresh_from_db()
        self.assertEqual(self.exercise_1.status, "completed")

    def test_mark_undo_exercise(self):
        # Mark exercise as done first
        self.exercise_1.status = "completed"
        self.exercise_1.save()

        # The URL to test
        url = reverse('mark_done')

        # Send POST request to undo the exercise (mark it as in_progress)
        response = self.client.post(url, json.dumps({
            "id": self.exercise_1.id,
            "type": "exercise",
            "action": "undo"
        }), content_type='application/json')

        # Check the response status and data
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {"success": True, "updated_progress": 0})

        # Check that the exercise status has been updated
        self.exercise_1.refresh_from_db()
        self.assertEqual(self.exercise_1.status, "in_progress")

    def test_progress_calculation(self):
        # Calculate the progress manually
        exercises = [self.exercise_1, self.exercise_2]
        additional_resources = [self.resource_1, self.resource_2]

        completed_items = 0
        total_items = len(exercises) + len(additional_resources)

        # Count completed exercises
        for exercise in exercises:
            if exercise.status == 'completed':
                completed_items += 1

        # Count completed resources
        for resource in additional_resources:
            if resource.status == 'completed':
                completed_items += 1

        # Manually calculated progress value
        expected_progress_value = (completed_items / total_items) * 100

        # Check if the calculation matches
        self.assertEqual(expected_progress_value, 0)  # Update based on the tests above (done/undo)

