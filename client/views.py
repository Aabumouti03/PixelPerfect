from django.shortcuts import render, redirect, get_object_or_404
from users.models import User, EndUser, UserProgramEnrollment
from client.models import Module
from django.contrib.auth import authenticate, login, logout
from .forms import ProgramForm 
from .models import Program, ProgramModule
from .models import Program
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Max
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

# Create your views here.
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

def users_management(request):
    users = User.objects.all()
    return render(request, 'client/users_management.html', {'users': users})  

def programs(request):
    programs = Program.objects.prefetch_related('program_modules__module').all()
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

            for index, module_id in enumerate(module_ids, start=1):
                try:
                    module = Module.objects.get(id=module_id)
                    ProgramModule.objects.create(program=program, module=module, order=index)
                except Module.DoesNotExist:
                    pass

            return redirect("programs")
    else:
        form = ProgramForm()
    return render(request, 'client/create_program.html', {'form': form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('users:log_in')

    return render(request, 'client/client_dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})


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
        if "remove_user" in request.POST:
            user_id = request.POST.get("remove_user")
            enrollment = enrolled_users.filter(user_id=user_id).first()
            if enrollment:
                enrollment.delete()
            return redirect("program_detail", program_id=program.id)
        if "add_users" in request.POST:
            users_to_add = request.POST.getlist("users_to_add")
            for enduser_id in users_to_add:
                if not enrolled_users.filter(user_id=enduser_id).exists():
                    UserProgramEnrollment.objects.create(
                        user_id=enduser_id,
                        program=program
                    )
            return redirect("program_detail", program_id=program.id)

    context = {
        "program": program,
        "all_modules": all_modules,
        "program_modules": program_modules,  
        "program_module_ids": program_module_ids, 
        "enrolled_users": enrolled_users,
        "all_users": EndUser.objects.all(),
        "enrolled_user_ids": enrolled_user_ids,
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