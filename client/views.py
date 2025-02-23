from django.shortcuts import render, redirect, get_object_or_404
from client.models import Program, Module

# Create your views here.

def CreateModule(request):
    modules = Module.objects.all()  # Fetch all available modules
    return render(request, "Module/Edit_Add_Module.html", {"modules": modules})

def EditModule(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "Module/Edit_Module.html", {"module": module})

def AddModule(request):
    return render(request, "Module/Add_Module.html")

