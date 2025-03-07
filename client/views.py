
from django.shortcuts import render, redirect, get_object_or_404
from users.models import User, EndUser, UserProgramEnrollment
from client.models import Module, Category
from collections import Counter
import json
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question, Module,  Program, ProgramModule
from users.models import Questionnaire_UserResponse, QuestionResponse, User
from django.core.paginator import Paginator
from .forms import ProgramForm, CategoryForm
from .models import Program, ProgramModule, Category
from client.statistics import * 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import csv

def admin_check(user):
    return user.is_authenticated and user.is_superuser


# Create your views here.
def client_dashboard(request):

    # GENERAL STATISTICS IN THE DASHBOARD
    enrollment_labels, enrollment_data = get_module_enrollment_stats()  
    last_work_time_labels, last_work_time_data = get_users_last_work_time()
    users_count = EndUser.objects.all()

    return render(request, 'client/client_dashboard.html' , {
        'users_count':len(users_count),
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
    programs = Program.objects.prefetch_related('program_modules__module').all()
    return render(request, 'client/programs.html', {'programs': programs})

@login_required
@user_passes_test(admin_check)
def create_program(request):
    categories = Category.objects.all()

    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_title = form.cleaned_data.get("title")

            if Program.objects.filter(title__iexact=program_title).exists():
                form.add_error("title", "A program with this title already exists.")

            else:
                program = form.save(commit=False)
                program.save()

            
                module_order = request.POST.get("module_order", "").strip()
                if module_order:
                    module_ids = module_order.split(",")
                    ProgramModule.objects.filter(program=program).delete()

                    for index, module_id in enumerate(module_ids, start=1):
                        if module_id.isdigit(): #making sure the javascript works properly
                            module = Module.objects.filter(id=int(module_id)).first()
                            if module:
                                ProgramModule.objects.create(program=program, module=module, order=index)

                return redirect("programs")

    else:
        form = ProgramForm()

    return render(request, "client/create_program.html", {
        "form": form,
        "categories": categories,
    })

@login_required
@user_passes_test(admin_check)
def log_out_client(request):
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

    
    return redirect('/client_dashboard/')


def program_detail(request, program_id): 
    program = get_object_or_404(Program, id=program_id)
    all_modules = Module.objects.all()
    program_modules = program.program_modules.all()  
    program_module_ids = list(program_modules.values_list('module_id', flat=True)) 

    enrolled_users = program.enrolled_users.all()
    enrolled_user_ids = set(enrollment.user_id for enrollment in enrolled_users)

    if request.method == "POST":
        if "remove_module" in request.POST:
            module_id = request.POST.get("remove_module")
            program_module = ProgramModule.objects.filter(program=program, module_id=module_id).first()
            if program_module:
                program_module.delete()
            return redirect("program_detail", program_id=program.id)

        if "add_modules" in request.POST:
            modules_to_add = request.POST.getlist("modules_to_add")
            max_order = program.program_modules.aggregate(Max('order'))['order__max'] or 0
            for index, m_id in enumerate(modules_to_add, start=1):
                module_obj = get_object_or_404(Module, id=m_id)
                ProgramModule.objects.create(program=program, module=module_obj, order=max_order + index)
            return redirect("program_detail", program_id=program.id)

    context = {
        "program": program,
        "all_modules": all_modules,
        "program_modules": program_modules,  
        "program_module_ids": program_module_ids,
        "enrolled_users": enrolled_users,
    }

    return render(request, "client/program_detail.html", context)

@csrf_exempt
def update_module_order(request, program_id):
    """Handles module reordering in a program while preventing UNIQUE constraint errors."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            program = get_object_or_404(Program, id=program_id)
            order_mapping = {int(item["id"]): index + 1 for index, item in enumerate(data["order"])}

            with transaction.atomic():
                temp_order = 1000  
                for module_id in order_mapping.keys():
                    ProgramModule.objects.filter(id=module_id, program=program).update(order=temp_order)
                    temp_order += 1 

                for module_id, new_order in order_mapping.items():
                    ProgramModule.objects.filter(id=module_id, program=program).update(order=new_order)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')


def category_list(request):
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    
    return render(request, 'client/category_list.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    programs = category.programs.all()
    modules = category.modules.all()

    context = {
        'category': category,
        'programs': programs,
        'modules': modules,
    }

    return render(request, 'client/category_detail.html', context)

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()

            modules = form.cleaned_data['modules']
            programs = form.cleaned_data['programs']

            category.modules.set(modules)
            category.programs.set(programs)

            return redirect('category_list')
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }

    return render(request, 'client/create_category.html', context)

def reports(request):
    # THREE CATEGORIES USERS - MODULES - PROGRAMMS 
    enrollment_labels, enrollment_data = get_module_enrollment_stats() # 1 for modules 
    last_work_labels, last_work_data = get_users_last_work_time() #  2 for users
    program_labels, program_data = get_program_enrollment_stats() # 3 for programs

    return render(request, 'client/reports.html', {
            'enrollment_labels': json.dumps(enrollment_labels),
            'enrollment_data': json.dumps(enrollment_data),  
            'last_work_labels': json.dumps(last_work_labels),
            'last_work_data': json.dumps(last_work_data),
            'program_labels': json.dumps(program_labels),
            'program_data': json.dumps(program_data),
        })

def modules_statistics(request):
    """Main view function to fetch and pass module statistics."""
    enrollment_labels, enrollment_data = get_module_enrollment_stats()
    completion_labels, completed_data, in_progress_data = get_module_completion_stats()
    avg_completion_labels, avg_completion_data = get_average_completion_percentage()
    modules_count = get_modules_count()

    return render(request, 'client/modules_statistics.html', {
        'modules_count': modules_count,
        'enrollment_labels': json.dumps(enrollment_labels),
        'enrollment_data': json.dumps(enrollment_data),
        'completion_labels': json.dumps(completion_labels),
        'completed_data': json.dumps(completed_data),
        'in_progress_data': json.dumps(in_progress_data),
        'completion_time_labels': json.dumps(avg_completion_labels),
        'completion_time_data': json.dumps(avg_completion_data),  
    })

def programs_statistics(request):
    """Main view function to fetch and pass program statistics."""
    
    program_labels, program_data = get_program_enrollment_stats()
    completion_labels, completed_data, in_progress_data = get_program_completion_stats()
    avg_completion_labels, avg_completion_data = get_average_program_completion_percentage()
    programs_count = get_programs_count()

    return render(request, 'client/programs_statistics.html', {
        'program_labels': json.dumps(program_labels),
        'program_data': json.dumps(program_data),
        'completion_labels': json.dumps(completion_labels),
        'completed_data': json.dumps(completed_data),
        'in_progress_data': json.dumps(in_progress_data),
        'completion_time_labels': json.dumps(avg_completion_labels),
        'completion_time_data': json.dumps(avg_completion_data),  
        'programs_count': programs_count
    })

'''
The userStatistics method is responsible for generating user statistics for reports. 
It gathers various metrics about users and their enrollments in programs and 
returns them in a JSON format to be displayed in the User Statistics Dashboard.

'''
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



def export_modules_statistics_csv(request):
    """Generate a CSV report of module statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="modules_statistics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
    modules_count = get_modules_count()
    writer.writerow(["Total Modules", modules_count])

    enrollment_labels, enrollment_data = get_module_enrollment_stats()
    for label, value in zip(enrollment_labels, enrollment_data):
        writer.writerow([f"Enrollment - {label}", value])

    completion_labels, completed_data, in_progress_data = get_module_completion_stats()
    for label, comp, in_prog in zip(completion_labels, completed_data, in_progress_data):
        writer.writerow([f"Completion - {label} (Completed)", comp])
        writer.writerow([f"Completion - {label} (In Progress)", in_prog])

    avg_completion_labels, avg_completion_data = get_average_completion_percentage()
    for label, value in zip(avg_completion_labels, avg_completion_data):
        writer.writerow([f"Avg Completion - {label}", value])

    return response

def export_programs_statistics_csv(request):
    """Generate a CSV report of program statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="programs_statistics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
    programs_count = get_programs_count()
    writer.writerow(["Total Programs", programs_count])

    enrollment_labels, enrollment_data = get_program_enrollment_stats()
    for label, value in zip(enrollment_labels, enrollment_data):
        writer.writerow([f"Enrollment - {label}", value])

    completion_labels, completed_data, in_progress_data = get_program_completion_stats()
    for label, comp, in_prog in zip(completion_labels, completed_data, in_progress_data):
        writer.writerow([f"Completion - {label} (Completed)", comp])
        writer.writerow([f"Completion - {label} (In Progress)", in_prog])

    avg_completion_labels, avg_completion_data = get_average_program_completion_percentage()
    for label, value in zip(avg_completion_labels, avg_completion_data):
        writer.writerow([f"Avg Completion - {label}", value])

    return response

def export_user_statistics_csv(request):
    """Generate a CSV report of user statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_statistics.csv"'

    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
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

    # Writing the statistics to the CSV file
    writer.writerow(["Total Users", total_users])
    writer.writerow(["Active Users", active_users])
    writer.writerow(["Inactive Users", inactive_users])
    writer.writerow(["Total Programs Enrolled", total_programs_enrolled])

    # Gender distribution
    for gender, count in gender_counts.items():
        writer.writerow([f"Gender - {gender}", count])

    # Ethnicity distribution
    for ethnicity, count in ethnicity_counts.items():
        writer.writerow([f"Ethnicity - {ethnicity}", count])

    # Sector distribution
    for sector, count in sector_counts.items():
        writer.writerow([f"Sector - {sector}", count])

    return response
