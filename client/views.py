from django.shortcuts import render, redirect, get_object_or_404
from users.models import User
from client.models import Module
from django.contrib.auth import authenticate, login, logout
from .forms import ProgramForm 
from .models import Program

# Create your views here.
def client_dashboard(request):
    return render(request, 'client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
    return render(request, 'users_management.html', {'users': users})

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

    return render(request, "modules_management.html", {"modules": modules_list})

def users_management(request):
    users = User.objects.all()
    return render(request, 'users_management.html', {'users': users})
    

def programs(request):
    programs = Program.objects.all()
    return render(request, 'programs.html', {'programs': programs})

def create_program(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('programs')
    else:
        form = ProgramForm()
    
    return render(request, 'create_program.html', {'form': form})


def log_out(request):
    """Confirm logout. If confirmed, redirect to welcome page. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('welcome_page')

    return render(request, 'client_dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})

def program_detail(request, program_id):
    """ View details of a single program """
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'program_detail.html', {'program': program})

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')