from django.shortcuts import render, redirect
from .forms import ProgramForm
from .models import Module, ProgramModule
from django.contrib.auth import logout

def dashboard(request):
    return render(request, 'client/dashboard.html')

def modules(request):
    return render(request, 'client/modules.html')

def users(request):
    return render(request, 'client/users.html')

def programs(request):
    return render(request, 'client/all_programs.html')

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

