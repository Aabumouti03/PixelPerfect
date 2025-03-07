from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from client.models import Module, Exercise, AdditionalResource, Section
from users.models import EndUser

class ModuleOverviewViewTest(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Create a Module
        self.module = Module.objects.create(title="Test Module", description="Test Module Description")

        # Create exercises and add them to a Section
        self.exercise_1 = Exercise.objects.create(title="Exercise 1", exercise_type="fill_blank", status="completed")
        self.exercise_2 = Exercise.objects.create(title="Exercise 2", exercise_type="multiple_choice", status="in_progress")
        section = Section.objects.create(title="Section 1", description="Section Description")
        section.exercises.add(self.exercise_1, self.exercise_2)
        self.module.sections.add(section)

        # Create additional resources
        self.resource_1 = AdditionalResource.objects.create(title="Resource 1", resource_type="book", status="completed")
        self.resource_2 = AdditionalResource.objects.create(title="Resource 2", resource_type="pdf", status="in_progress")
        self.module.additional_resources.add(self.resource_1, self.resource_2)

        # Create EndUser
        self.end_user = EndUser.objects.create(user=self.user)

        # Log the user in
        self.client.login(username='testuser', password='testpassword')

    def test_module_overview_view(self):
        # The URL to test
        url = reverse('module_overview', kwargs={'module_id': self.module.id})

        # Perform GET request
        response = self.client.get(url)

        # Check the response status
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'users/moduleOverview.html')

        # Check the context values
        self.assertIn('module', response.context)
        self.assertEqual(response.context['module'], self.module)
        self.assertIn('exercises', response.context)
        self.assertEqual(len(response.context['exercises']), 2)  # There are 2 exercises
        self.assertIn('additional_resources', response.context)
        self.assertEqual(len(response.context['additional_resources']), 2)  # There are 2 resources
        self.assertIn('progress_value', response.context)
        self.assertEqual(response.context['progress_value'], 50)  # Progress value should be 50%

    def test_progress_calculation(self):
        # Calculate progress manually
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
        self.assertEqual(expected_progress_value, 50)

