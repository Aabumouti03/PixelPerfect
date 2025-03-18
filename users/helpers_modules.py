from client.models import Module, Exercise, AdditionalResource,ProgramModule  
from users.models import EndUser, UserModuleProgress, UserProgramProgress

def calculate_progress(end_user, module):
    """Calculate the progress of a module based on completed exercises, additional resources, and videos."""
    
    exercises = []
    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())

    # Count completed exercises
    completed_exercises = [exercise for exercise in exercises if exercise.status == 'completed']

    # Count completed resources
    completed_resources = [resource for resource in module.additional_resources.all() if resource.status == 'completed']

    # Count completed videos
    completed_videos = [video for video in module.video_resources.all() if video.status == 'completed']

    # Calculate total and completed items
    total_items = len(exercises) + module.additional_resources.count() + module.video_resources.count()
    completed_items = len(completed_exercises) + len(completed_resources) + len(completed_videos)

    # Calculate progress percentage
    progress = (completed_items / total_items) * 100 if total_items > 0 else 0

    return round(progress, 2)  # Round to 2 decimal places for better accuracy


def calculate_program_progress(end_user, program):
    # Get all modules in the program
    program_modules = ProgramModule.objects.filter(program=program)

    # Calculate the number of completed modules
    completed_modules = 0
    total_modules = program_modules.count()

    for program_module in program_modules:
        module = program_module.module
        # Check if the module is completed
        user_module_progress = UserModuleProgress.objects.filter(user=end_user, module=module).first()
        if user_module_progress and user_module_progress.completion_percentage == 100:
            completed_modules += 1

    # Calculate progress percentage
    if total_modules > 0:
        progress = (completed_modules / total_modules) * 100
    else:
        progress = 0

    return progress

def update_user_program_progress(end_user, program):
    progress = calculate_program_progress(end_user, program)
    
    # Get or create the user program progress object
    user_program_progress, created = UserProgramProgress.objects.get_or_create(user=end_user, program=program)
    
    # Update the completion percentage of the user for the program
    user_program_progress.completion_percentage = progress
    user_program_progress.save()