from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question, Module,  Program, ProgramModule
from users.models import Questionnaire_UserResponse, QuestionResponse, User
from django.core.paginator import Paginator
from .forms import ProgramForm 
from .models import Program, ProgramModule, Category

from django.contrib.auth.decorators import login_required, user_passes_test

def admin_check(user):
    return user.is_authenticated and user.is_superuser


# Create your views here.
def client_dashboard(request):
    return render(request, 'client/client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
    return render(request, 'client/users_management.html', {'users': users})
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
    return render(request, "client/modules_management.html", {"modules": modules_list})

def users_management(request):
    users = User.objects.all()
    return render(request, 'client/users_management.html', {'users': users})
    

def programs(request):
    programs = Program.objects.all()
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
    """ View details of a single program """
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'program_detail.html', {'program': program})

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')
