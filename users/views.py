from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import StickyNote, EndUser
import json

@csrf_exempt
@login_required
def save_notes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')

        # Get the EndUser instance for the logged-in user
        end_user = EndUser.objects.get(user=request.user)

        # Get or create the sticky note for the current user
        sticky_note, created = StickyNote.objects.get_or_create(user=end_user)
        sticky_note.content = content
        sticky_note.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_notes(request):
    try:
        # Get the EndUser instance for the logged-in user
        end_user = EndUser.objects.get(user=request.user)
        sticky_note = StickyNote.objects.get(user=end_user)
        return JsonResponse({'success': True, 'content': sticky_note.content})
    except StickyNote.DoesNotExist:
        return JsonResponse({'success': True, 'content': ''})  # Return empty content if no note exists
    


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
    return render(request, 'users/dashboard.html', context)

def modules(request):
    return render(request, 'users/modules.html')

def profile(request):
    return render(request, 'users/profile.html')

def logout_view(request):
    return render(request, 'users/logout.html')