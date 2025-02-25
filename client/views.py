from django.shortcuts import render, redirect, get_object_or_404
from client.models import Program, Module
from django.shortcuts import render, get_object_or_404
from client.models import Module

def CreateModule(request):
    modules = Module.objects.all()
    return render(request, "Module/Edit_Add_Module.html", {"modules": modules})

def EditModule(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "Module/Edit_Module.html", {"module": module})

def AddModule(request):
    return render(request, "Module/Add_Module.html")


def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def users(request):
    return render(request, 'users.html')

def programs(request):
    return render(request, 'programs.html')

def logout_view(request):
    return render(request, 'logout.html')

