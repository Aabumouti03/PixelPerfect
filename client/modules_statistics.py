from users.models import UserModuleEnrollment, UserModuleProgress, EndUser, UserProgramEnrollment
from client.models import Module, Program
from django.db.models import Count, Avg

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
        UserModuleProgress.objects.values('module__title', 'status')
        .annotate(count=Count('id'))
    )

    completion_data = {title: {'completed': 0, 'in_progress': 0} for title in all_modules}
    for entry in completion_stats:
        module = entry['module__title']
        status = entry['status']
        if status == 'completed':
            completion_data[module]['completed'] = entry['count']
        else:
            completion_data[module]['in_progress'] += entry['count']

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

# this is for users 
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