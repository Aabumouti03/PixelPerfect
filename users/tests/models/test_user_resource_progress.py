from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import EndUser, UserResourceProgress
from client.models import AdditionalResource

User = get_user_model()

class UserResourceProgressTest(TestCase):
    def test_resource_progress(self):
        user = User.objects.create_user(username='resourceuser', password='pass')
        end_user = EndUser.objects.create(user=user)
        resource = AdditionalResource.objects.create(
            resource_type='book',
            title="Extra Resource",
            description="Resource content"
        )

        progress = UserResourceProgress.objects.create(user=end_user, resource=resource, status='in_progress')
        self.assertEqual(str(progress), "resourceuser - Extra Resource: in_progress")

        with self.assertRaises(Exception):
            UserResourceProgress.objects.create(user=end_user, resource=resource)