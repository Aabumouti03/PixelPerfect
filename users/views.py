from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSignUpForm, LogInForm, EndUserProfileForm
from django.shortcuts import render, get_object_or_404
from client.models import Module,  ModuleRating, Exercise, AdditionalResource, Section
from users.models import UserModuleProgress, UserModuleEnrollment, EndUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.models import User  
import os
from django.conf import settings
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Avg
from .helpers import calculate_progress  




#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'users/welcome_page.html')

def dashboard(request):
    return render(request, 'users/dashboard.html')
    return render(request, 'users/dashboard.html')

def modules(request):
    return render(request, 'users/modules.html')
    return render(request, 'users/modules.html')

def profile(request):
    return render(request, 'users/profile.html')
    return render(request, 'users/profile.html')

def welcome_page(request):
    return render(request, 'users/welcome_page.html')

def about(request):
    return render(request, 'users/about.html')

def contact_us(request):
    return render(request, 'users/contact_us.html')

def log_in(request):
    """Log in page view function"""
    if request.method == "POST":
        form = LogInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LogInForm()

    return render(request, 'users/log_in.html', {'form': form})


#A function for displaying a sign up page
def sign_up_step_1(request):
    """Handles Step 1: User Account Details"""
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():

            request.session['user_form_data'] = user_form.cleaned_data
            return redirect('sign_up_step_2')
    
    else:
        user_form_data = request.session.get('user_form_data', {})
        user_form = UserSignUpForm(initial=user_form_data) 

    return render(request, 'users/sign_up_step_1.html', {'user_form': user_form})

def sign_up_step_2(request):
    """Handles Step 2: Profile Details"""
    if 'user_form_data' not in request.session:
        return redirect('sign_up_step_1')

    if request.method == "POST":
        profile_form = EndUserProfileForm(request.POST)
        if profile_form.is_valid():

            user_data = request.session.pop('user_form_data')
            user_form = UserSignUpForm(data=user_data)
            if user_form.is_valid():
                user = user_form.save()
                

                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()

                return redirect('log_in')

    else:
        profile_form = EndUserProfileForm()

    return render(request, 'users/sign_up_step_2.html', {'profile_form': profile_form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

    # if user cancels, stay on the same page
    return render(request, 'users/dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})


def forget_password(request):
    return render(request, 'users/forget_password.html')

def password_reset_sent(request, reset_id):
    return render(request, 'users/password_reset_sent.html')

def reset_password(request, reset_id):
    return render(request, 'users/reset_password.html')



@login_required
def exercise_detail(request, exercise_id):
    """Fetch the exercise details, including questions, saved responses, and the related diagram."""

    exercise = get_object_or_404(Exercise, id=exercise_id)

    user, created = EndUser.objects.get_or_create(user=request.user)

    

    # Find a **single** diagram from sections linked to this exercise
    diagram = None
    for section in exercise.sections.all():
        if section.diagram:  
            diagram = section.diagram  
            break  # ✅ Stop at the first diagram found

    if request.method == 'POST':
        for question in exercise.questions.all():
            answer_text = request.POST.get(f'answer_{question.id}', '').strip()


        return redirect('exercise_detail', exercise_id=exercise.id)

    return render(request, 'users/exercise_detail.html', {
        'exercise': exercise,
        'diagram': diagram,  # ✅ Pass the diagram to template
    })




@login_required
def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises and additional resources."""
    
    # Get the module
    module = get_object_or_404(Module, id=module_id)

    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    # Get all exercises and resources associated with the module
    exercises = []
    additional_resources = list(module.additional_resources.all())

    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())

    # Initialize the number of completed items
    completed_items = 0
    total_items = len(exercises) + len(additional_resources)

    # Count completed exercises for the user
    for exercise in exercises:
        if exercise.status=='completed':
            completed_items += 1

    # Count completed additional resources for the user
    for resource in additional_resources:
        if resource.status=='completed':
            completed_items += 1

    # Calculate completion percentage
    progress_value = 0
    if total_items > 0:
        progress_value = (completed_items / total_items) * 100

    # Get or create a UserModuleProgress entry for the module
    user_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
    user_progress.completion_percentage = progress_value
    user_progress.save()

    # Pass progress value and related objects to the template
    context = {
        'module': module,
        'exercises': exercises,
        'additional_resources': additional_resources,
        'progress_value': progress_value,  # Show the updated progress
    }

    return render(request, 'users/moduleOverview.html', context)


@login_required
def mark_done(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("id")
        item_type = data.get("type")
        action = data.get("action")  # 'done' or 'undo'

        user = request.user
        end_user = EndUser.objects.get(user=user)  # Get the EndUser instance associated with the user

        if item_type == "resource":
            resource = AdditionalResource.objects.get(id=item_id)
            if resource.status == 'completed':
                resource.status = 'in_progress'
            else:
                resource.status = 'completed'
            resource.save()
            module = Module.objects.filter(additional_resources=resource).first()

        elif item_type == "exercise":
            exercise = Exercise.objects.get(id=item_id)
            if exercise.status == 'completed':
                exercise.status = 'in_progress'
            else:
                exercise.status = 'completed'
            exercise.save()
            module = exercise.sections.first().modules.first()

        # Recalculate the progress and update the user module progress
        user_module_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
        user_module_progress.completion_percentage = calculate_progress(end_user, module)
        user_module_progress.save()

        # Return the updated progress as JSON
        return JsonResponse({
            "success": True,
            "updated_progress": user_module_progress.completion_percentage
        })

    return JsonResponse({"success": False})






@login_required
def user_modules(request):
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user)

    background_folder = os.path.join(settings.BASE_DIR, 'static/img/backgrounds')
    
    background_images = os.listdir(background_folder)
    
    module_data = []

    for enrollment in enrolled_modules:
        module = enrollment.module
        progress = UserModuleProgress.objects.filter(user=end_user, module=module).first()

        progress_percentage = progress.completion_percentage if progress else 0

        background_image = random.choice(background_images)

        module_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "progress": progress_percentage,
            "background_image": f'img/backgrounds/{background_image}' 
        })

    return render(request, 'users/userModules.html', {"module_data": module_data})



def all_modules(request):
    modules = Module.objects.all()

    return render(request, 'users/all_modules.html', {'modules': modules})

@csrf_exempt  # Remove this if you're using CSRF protection in JS
def rate_module(request, module_id):
    """Handles AJAX-based user rating for a module."""
    if request.method == "POST" and request.user.is_authenticated:
        module = get_object_or_404(Module, id=module_id)
        try:
            data = json.loads(request.body)
            rating_value = int(data.get("rating", 0))

            if 1 <= rating_value <= 5:
                # ✅ Corrected access to the EndUser profile
                end_user = request.user.User_profile  # Access related_name from EndUser model

                # Save or update rating
                rating_obj, created = ModuleRating.objects.update_or_create(
                    user=end_user,  # ✅ Use the correct reference to the EndUser instance
                    module=module,
                    defaults={'rating': rating_value}
                )

                # Recalculate average rating
                average_rating = module.ratings.aggregate(Avg('rating'))['rating__avg']
                average_rating = round(average_rating, 1) if average_rating else 0

                return JsonResponse({"success": True, "average_rating": average_rating})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"})

    return JsonResponse({"success": False, "message": "Invalid request or unauthorized user"})

