from django.shortcuts import render, redirect, get_object_or_404
from client.models import Program, Module
from django.shortcuts import render, get_object_or_404
from client.models import Module
from .forms import ModuleForm, SectionForm
from .models import Module, Section, Exercise, Question
from django.db import transaction
from django.http import JsonResponse


def CreateModule(request):
    modules = Module.objects.prefetch_related("sections__exercises__questions").all()
    return render(request, "Module/Edit_Add_Module.html", {"modules": modules})

def EditModule(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "Module/edit_module.html", {"module": module})

def add_module(request):
    """Handles adding a module with multiple sections."""
    form_data = request.session.get('module_form_data', {})  # Load stored data
    form = ModuleForm(initial=form_data) if form_data else ModuleForm()

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.save()
            form.save_m2m()  # Save many-to-many relationship
            
            request.session.pop('module_form_data', None)  # Clear stored data after save
            return redirect('modules')  

        request.session['module_form_data'] = request.POST  # Save form data if invalid

    sections = Section.objects.all()
    return render(request, 'Module/add_module.html', {'form': form, 'sections': sections})

def add_section(request):
    """Handles the addition of a new section with title and description."""
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save() 
            return redirect('add_module') 

    else:
        form = SectionForm() 
        
    return render(request, 'Module/add_section.html', {'form': form})

def get_sections(request):
    """Returns all sections as JSON (for dynamically updating dropdown)."""
    sections = list(Section.objects.values('id', 'title'))
    return JsonResponse({'sections': sections})
   

def programs(request):
    return render(request, 'client/programs.html')

def logout_view(request):
    return render(request, 'client/logout.html')

def client_dashboard(request):
    return render(request, 'client/client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
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
