from client.models import Module, Exercise, AdditionalResource  # Import models from the 'client' app
from users.models import EndUser  # Import EndUser model

def calculate_progress(end_user, module):
  
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