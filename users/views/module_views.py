from django.shortcuts import render, get_object_or_404
from client.models import Module, Exercise

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')

def logout_view(request):
    return render(request, 'logout.html')

def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises."""
    
    # ✅ Get the module object, or return 404 if not found
    module = get_object_or_404(Module, id=module_id)

    # ✅ Collect all exercises from the module’s sections
    exercises = []
    for section in module.sections.all():
        exercises.extend(section.exercises.all())

    context = {
        'module': module,
        'exercises': exercises,  # ✅ Pass exercises to template
        'progress_value': 50  # ✅ Example progress value
    }
    
    return render(request, 'moduleOverview.html', context)

def exercise_detail(request, exercise_id):
    """Fetch the exercise by ID and render its details."""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    context = {
        'exercise': exercise,
    }
    
    return render(request, 'exercise_detail.html', context)
