from django.shortcuts import render, get_object_or_404
from client.models import Module, Exercise, AdditionalResource
from users.forms.users.moduleForms import ExerciseAnswerForm
from django.contrib.auth.decorators import login_required 
from users.models import ExerciseResponse,EndUser
from django.contrib.auth import get_user_model


# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')


def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises and additional resources."""
    
    # ✅ Get the module object, or return 404 if not found
    module = get_object_or_404(Module, id=module_id)

    # ✅ Collect all exercises from the module’s sections
    exercises = []
    additional_resources = []
    
    for section in module.sections.all():
        exercises.extend(section.exercises.all())
        additional_resources.extend(section.additional_resources.all())

    context = {
        'module': module,
        'exercises': exercises,  # ✅ Pass exercises to template
        'additional_resources': additional_resources,  # ✅ Pass additional resources to template
        'progress_value': 50  # ✅ Example progress value
    }
    
    return render(request, 'users/moduleOverview.html', context)



def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)

    # Ensure request.user is an EndUser instance
    User = get_user_model()  # Dynamically get the correct user model

    user, created = EndUser.objects.get_or_create(user=request.user)


    # Retrieve existing answers for this user
    saved_responses = {
        response.question.id: response.response_text
        for response in ExerciseResponse.objects.filter(user=user, question__in=exercise.questions.all())
    }

    if request.method == 'POST':
        for question in exercise.questions.all():
            answer_text = request.POST.get(f'answer_{question.id}', '').strip()

            # Update existing response or create a new one
            response_obj, created = ExerciseResponse.objects.update_or_create(
                user=user,  # ✅ Ensure this is an EndUser instance
                question=question,
                defaults={'response_text': answer_text}
            )

        return redirect('users/exercise_detail', exercise_id=exercise.id)

    return render(request, 'users/exercise_detail.html', {
        'exercise': exercise,
        'saved_responses': saved_responses,
    })