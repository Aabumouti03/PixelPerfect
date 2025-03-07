from django.urls import reverse

def reverse_with_next(url_name, next_url):
    """Extended version of reverse to generate URLs with redirects"""
    url = reverse(url_name)
    url += f"?next={next_url}"
    return url


class LogInTester:
    """Class support login in tests."""
 
    def _is_logged_in(self):
        """Returns True if a user is logged in.  False otherwise."""

        return '_auth_user_id' in self.client.session.keys()

    
def calculate_progress(end_user, module):
    # Get all exercises in the module
    exercises = []
    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())

    # Count completed exercises
    completed_exercises = [exercise for exercise in exercises if exercise.status == 'completed']

    # Count completed resources
    completed_resources = [resource for resource in module.additional_resources.all() if resource.status == 'completed']

    # Calculate total and completed items
    total_items = len(exercises) + module.additional_resources.count()
    completed_items = len(completed_exercises) + len(completed_resources)

    # Calculate progress percentage
    if total_items > 0:
        progress = (completed_items / total_items) * 100
    else:
        progress = 0

    return progress
