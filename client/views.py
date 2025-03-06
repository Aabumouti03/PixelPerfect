from django.shortcuts import render, redirect, get_object_or_404
from users.models import User, EndUser, UserProgramEnrollment
from client.models import Module
from django.contrib.auth import authenticate, login, logout
from .forms import ProgramForm 
from .models import Program
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def client_dashboard(request):
    return render(request, 'client/client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
    return render(request, 'client/users_management.html', {'users': users})
#####################
def module_overview(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "client/moduleOverview.html", {"module": module})

def client_modules(request):
    modules = Module.objects.all().values("id", "title")  # Include "id"
    module_colors = ["color1", "color2", "color3", "color4", "color5", "color6"]
    
    modules_list = []
    for index, module in enumerate(modules):
        module_data = {
            "id": module["id"],  # Add "id"
            "title": module["title"],
            "color_class": module_colors[index % len(module_colors)]
        }
        modules_list.append(module_data)

    return render(request, "client/client_modules.html", {"modules": modules_list})


def edit_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    
    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('client_modules')  # Redirect back to module management
    
    else:
        form = ModuleForm(instance=module)

    return render(request, 'client/edit_module.html', {'form': form, 'module': module})

def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.delete()
    return redirect("client_modules")

#####################
def users_management(request):
    users = User.objects.all()
    return render(request, 'client/users_management.html', {'users': users})
    

def programs(request):
    programs = Program.objects.all()
    return render(request, 'client/programs.html', {'programs': programs})

def create_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs')
    else:
        form = ProgramForm()
    
    return render(request, 'client/create_program.html', {'form': form})


def log_out(request):
    """Confirm logout. If confirmed, redirect to welcome page. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('welcome_page')

    return render(request, 'client/client_dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})

def program_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    all_modules = Module.objects.all()
    # This is a QuerySet of UserProgramEnrollment
    enrolled_users = program.enrolled_users.all()
    enrolled_user_ids = set(enrollment.user_id for enrollment in enrolled_users)

    
    if request.method == "POST":

        # 1) Remove a module
        if "remove_module" in request.POST:
            module_id = request.POST.get("remove_module")
            module_obj = get_object_or_404(Module, id=module_id)
            # Because program.modules is a real ManyToManyField, we can do:
            program.modules.remove(module_obj)
            return redirect("program_detail", program_id=program.id)

        # 2) Add modules
        if "add_modules" in request.POST:
            modules_to_add = request.POST.getlist("modules_to_add")
            for m_id in modules_to_add:
                module_obj = get_object_or_404(Module, id=m_id)
                program.modules.add(module_obj)
            return redirect("program_detail", program_id=program.id)

        # 3) Remove a user
        if "remove_user" in request.POST:
            user_id = request.POST.get("remove_user")
            # Find the enrollment row and delete it
            enrollment = enrolled_users.filter(user_id=user_id).first()
            if enrollment:
                enrollment.delete()
            return redirect("program_detail", program_id=program.id)

        # 4) Add users
        if "add_users" in request.POST:
            users_to_add = request.POST.getlist("users_to_add")
            for enduser_id in users_to_add:
                # Only create if not already enrolled
                if not enrolled_users.filter(user_id=enduser_id).exists():
                    UserProgramEnrollment.objects.create(
                        user_id=enduser_id,
                        program=program
                    )
            return redirect("program_detail", program_id=program.id)

    context = {
        "program": program,
        "all_modules": all_modules,
        "enrolled_users": enrolled_users,  # QuerySet of UserProgramEnrollment
        "all_users": EndUser.objects.all(),
        "enrolled_user_ids": enrolled_user_ids,  # <--- pass this
    }

    return render(request, "client/program_detail.html", context)


def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')