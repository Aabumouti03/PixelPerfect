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
    return render(request, 'client/dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})

