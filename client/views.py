from django.shortcuts import render
from users.models import User
from client.models import Module

# Create your views here.
def client_dashboard(request):
    return render(request, 'client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
    return render(request, 'users_management.html', {'users': users})

def modules_management(request):
    modules = Module.objects.all().values("title")  # Get module names
    module_colors = ["#CEE7F2", "#44778d", "#a7d4e8", "#ff5733", "#3498DB", "#2ECC71"]  # Add more colors

    modules_list = []
    for index, module in enumerate(modules):
        module["color"] = module_colors[index % len(module_colors)]
        modules_list.append(module)

    return render(request, "modules_management.html", {"modules": modules_list})