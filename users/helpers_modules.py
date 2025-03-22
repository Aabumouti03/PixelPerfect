from client.models import Module, Exercise, AdditionalResource,ProgramModule  
from users.models import EndUser, UserModuleProgress, UserProgramProgress, UserExerciseProgress, UserResourceProgress,UserVideoProgress

def calculate_progress(user, module):
    """Calculate the completion percentage for a user's progress in a module."""
    
    exercises = []
    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())
    additional_resources = list(module.additional_resources.all())
    video_resources = list(module.video_resources.all()) 

    completed_items = (
        UserExerciseProgress.objects.filter(user=user, exercise__in=exercises, status='completed').count() +
        UserResourceProgress.objects.filter(user=user, resource__in=additional_resources, status='completed').count() +
        UserVideoProgress.objects.filter(user=user, video__in=video_resources, status='completed').count()
    )
    

    total_items = len(exercises) + len(additional_resources) + len(video_resources)

    return (completed_items / total_items) * 100 if total_items > 0 else 0



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




