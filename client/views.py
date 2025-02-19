from django.shortcuts import render, redirect
from .forms import ProgramForm
from .models import Module, ProgramModule

def create_program(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.save()

            # Process module order
            module_order = request.POST.get("module_order", "")
            module_ids = module_order.split(",") if module_order else []

            # Clear existing program-module relationships if necessary
            program.program_modules.all().delete()

            # Add modules in the correct order
            for index, module_id in enumerate(module_ids, start=1):
                try:
                    module = Module.objects.get(id=module_id)
                    ProgramModule.objects.create(program=program, module=module, order=index)
                except Module.DoesNotExist:
                    pass  # Skip if module does not exist

            return redirect("temp")
    else:
        form = ProgramForm()

    return render(request, "client/create_program.html", {"form": form})

def temp(request):
    return render(request, "client/temp.html")