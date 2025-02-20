from django.shortcuts import render
from client.models import Module, Program

# Create your views here.

def dashboard(request):
    # Fetch the first program (or a specific program)
    program = Program.objects.first()  # Adjust this query as needed
    program_modules = program.modules.all() if program else []

    # Fetch all modules for the modules container
    modules = Module.objects.all()

     # Add progress data to modules (example: random progress for demonstration)
    for module in modules:
        module.progress = 50  # Replace with actual progress logic

    #total_exercises = module.exercises.count()
    #completed_exercises = module.user_progress.filter(status='completed').count()
    #module.progress = (completed_exercises / total_exercises) * 100 if total_exercises > 0 else 0

    context = {
        'user': request.user,
        'program': program,
        'program_modules': program_modules,
        'modules': modules,
    }
    return render(request, 'dashboard.html', context)

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')

def logout_view(request):
    return render(request, 'logout.html')