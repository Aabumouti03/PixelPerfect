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