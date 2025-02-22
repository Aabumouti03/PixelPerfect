from django.shortcuts import render, redirect, get_object_or_404
from users.models import User
from client.models import Module
from collections import Counter
import json
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress

from django.contrib.auth import authenticate, login, logout
from .forms import ProgramForm 
from .models import Program, ProgramModule, Module
import json
from client.modules_statistics import * 


# Create your views here.
def client_dashboard(request):

    # GENERAL STATISTICS IN THE DASHBOARD
    enrollment_labels, enrollment_data = get_module_enrollment_stats()  
    last_work_time_labels, last_work_time_data = get_users_last_work_time()

    return render(request, 'client/client_dashboard.html' , {
        'enrollment_labels': json.dumps(enrollment_labels),
        'enrollment_data': json.dumps(enrollment_data),
        'last_work_time_labels': json.dumps(last_work_time_labels),
        'last_work_time_data': json.dumps(last_work_time_data),
    })

def users_management(request):
    users = EndUser.objects.all()
    return render(request, 'client/users_management.html', {'users': users})

def modules_management(request):
    modules = Module.objects.all().values("title")
    module_colors = ["color1", "color2", "color3", "color4", "color5", "color6"]
    
    modules_list = []
    for index, module in enumerate(modules):
        module_data = {
            "title": module["title"],
            "color_class": module_colors[index % len(module_colors)]
        }
        modules_list.append(module_data)

    return render(request, "client/modules_management.html", {"modules": modules_list})

def programs(request):
    programs = Program.objects.all()
    return render(request, 'client/programs.html', {'programs': programs})

def logout_view(request):
    return render(request, 'client/logout.html')

def create_program(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.save()

            module_order = request.POST.get("module_order", "")
            module_ids = module_order.split(",") if module_order else []

            program.program_modules.all().delete()

            # Add modules in the correct order
            for index, module_id in enumerate(module_ids, start=1):
                try:
                    module = Module.objects.get(id=module_id)
                    ProgramModule.objects.create(program=program, module=module, order=index)
                except Module.DoesNotExist:
                    pass

            return redirect("programs")
    else:
        form = ProgramForm()

    return render(request, "client/create_program.html", {"form": form})


def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('users:log_in')

    # if user cancels, stay on the same page
    return render(request, 'client/client_dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})

def program_detail(request, program_id):
    """ View details of a single program """
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'program_detail.html', {'program': program})

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')



def userStatistics(request):
    total_users = EndUser.objects.count()
    active_users = EndUser.objects.filter(user__is_active=True).count()
    inactive_users = total_users - active_users
    total_programs_enrolled = UserProgramEnrollment.objects.count()

    # Get gender distribution
    gender_counts = dict(Counter(EndUser.objects.values_list('gender', flat=True)))
    
    # Get ethnicity distribution
    ethnicity_counts = dict(Counter(EndUser.objects.values_list('ethnicity', flat=True)))
    
    # Get sector distribution
    sector_counts = dict(Counter(EndUser.objects.values_list('sector', flat=True)))

    # Pass data as JSON
    stats_data = {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "programs_enrolled": total_programs_enrolled,
        "gender_distribution": gender_counts,
        "ethnicity_distribution": ethnicity_counts,
        "sector_distribution": sector_counts,
    }

    return render(request, "client/userStatistics.html", {"stats": json.dumps(stats_data)})  # ✅ Pass JSON data

