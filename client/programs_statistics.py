from users.models import EndUser, UserProgramEnrollment, UserProgramProgress
from client.models import Program
from django.db.models import Count, Avg

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
        UserProgramProgress.objects.values('program__title', 'status')
        .annotate(count=Count('id'))
    )

    completion_data = {title: {'completed': 0, 'in_progress': 0} for title in all_programs}

    for entry in completion_stats:
        program = entry['program__title']
        status = entry['status']
        if status == 'completed':
            completion_data[program]['completed'] = entry['count']
        else:
            completion_data[program]['in_progress'] += entry['count']

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