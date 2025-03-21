from users.models import EndUser, UserProgramEnrollment, UserProgramProgress, UserModuleEnrollment, UserModuleProgress
from client.models import Program, Module
from django.db.models import Count, Avg, Q


# Programs Statistics 

def get_program_enrollment_stats():    
    all_programs = Program.objects.values_list('id', 'title')

    programs_enrollments = (
        UserProgramEnrollment.objects
        .values('program__id', 'program__title')
        .annotate(count=Count('id'))
    )

    enrollment_data = {program_title: 0 for _, program_title in all_programs}

    for entry in programs_enrollments:
        program_title = entry['program__title']
        enrollment_data[program_title] = entry['count']

    labels = list(enrollment_data.keys())  
    data = list(enrollment_data.values())

    return labels, data

def get_program_completion_stats():
    """Fetch the completion statistics for each program, including those with 0% completion."""
    
    all_programs = Program.objects.values_list('title', flat=True)
    
    completion_stats = (
        UserProgramProgress.objects
        .values('program__title')
        .annotate(
            completed_count=Count('id', filter=Q(completion_percentage=100)),
            in_progress_count=Count('id', filter=Q(completion_percentage__lt=100))
        )
    )
    
    completion_data = {title: {'completed': 0, 'in_progress': 0} for title in all_programs}
    
    for entry in completion_stats:
        program = entry['program__title']
        completion_data[program]['completed'] = entry['completed_count']
        completion_data[program]['in_progress'] = entry['in_progress_count']
    
    labels = list(completion_data.keys())
    completed_data = [completion_data[p]['completed'] for p in labels]
    in_progress_data = [completion_data[p]['in_progress'] for p in labels]
    
    return labels, completed_data, in_progress_data

def get_average_program_completion_percentage():
    """Fetch the average completion percentage for each program, including those with 0% completion."""
    
    all_programs = Program.objects.values_list('title', flat=True)

    program_completion = (
        UserProgramProgress.objects
        .values('program__title')
        .annotate(avg_completion=Avg('completion_percentage')) 
    )

    completion_data = {program: 0 for program in all_programs}

    for entry in program_completion:
        completion_data[entry['program__title']] = entry['avg_completion'] or 0

    labels = list(completion_data.keys())
    data = list(completion_data.values())

    return labels, data

def get_programs_count():
    """Fetch the total number of programs."""
    return Program.objects.count()


# Modules Statistics 

def get_users_last_work_time():
    """Fetch number of users for each last work time category."""
    last_work_stats = (
        EndUser.objects.values("last_time_to_work")  
        .annotate(count=Count("id"))  
        .order_by("last_time_to_work")  # Keep the order consistent
    )

    labels = [entry["last_time_to_work"] for entry in last_work_stats]
    data = [entry["count"] for entry in last_work_stats]

    return labels, data

def get_module_enrollment_stats():    
    all_modules = Module.objects.values_list('id', 'title')

    module_enrollments = (
        UserModuleEnrollment.objects
        .values('module__id', 'module__title')
        .annotate(count=Count('id'))
    )

    enrollment_data = {module_title: 0 for _, module_title in all_modules}

    for entry in module_enrollments:
        module_title = entry['module__title']
        enrollment_data[module_title] = entry['count']

    labels = list(enrollment_data.keys())  
    data = list(enrollment_data.values())

    return labels, data

def get_module_completion_stats():
    all_modules = Module.objects.values_list('title', flat=True)
    
    completion_stats = (
        UserModuleProgress.objects
        .values('module__title')
        .annotate(
            completed_count=Count('id', filter=Q(completion_percentage=100)),
            in_progress_count=Count('id', filter=Q(completion_percentage__lt=100))
        )
    )
    
    completion_data = {title: {'completed': 0, 'in_progress': 0} for title in all_modules}
    
    for entry in completion_stats:
        module = entry['module__title']
        completion_data[module]['completed'] = entry['completed_count']
        completion_data[module]['in_progress'] = entry['in_progress_count']

    labels = list(completion_data.keys())
    completed_data = [completion_data[m]['completed'] for m in labels]
    in_progress_data = [completion_data[m]['in_progress'] for m in labels]
    
    return labels, completed_data, in_progress_data

def get_average_completion_percentage():
    all_modules = Module.objects.values_list('title', flat=True)

    module_completion = (
        UserModuleProgress.objects
        .values('module__title')
        .annotate(avg_completion=Avg('completion_percentage')) 
    )

    completion_data = {module: 0 for module in all_modules}

    for entry in module_completion:
        completion_data[entry['module__title']] = entry['avg_completion'] or 0 

    labels = list(completion_data.keys())
    data = list(completion_data.values())

    return labels, data

def get_modules_count():
    modules = Module.objects.all().values("title")
    return len(modules)
