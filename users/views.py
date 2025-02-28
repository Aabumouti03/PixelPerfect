from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSignUpForm, LogInForm, EndUserProfileForm
from django.shortcuts import render, get_object_or_404
from client.models import Module,  ModuleRating, Exercise, AdditionalResource, Section
from users.models import UserModuleProgress, UserModuleEnrollment, EndUser, UserResponse
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

# Create your views here.

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
            '''
            rememebr to vgange to this after testing
            if user is not None:
                login(request, user)
                return redirect('dashboard')
           '''
     

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

def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises and additional resources."""

    # ✅ Get the module object, or return 404 if not found
    module = get_object_or_404(Module, id=module_id)

    # ✅ Separate sections into exercises (diagram removed)
    exercises = []
    additional_resources = list(module.additional_resources.all())  # ✅ Retrieve additional resources

    for section in module.sections.all():
        if section.exercises.exists():  
            exercises.extend(section.exercises.all())  # ✅ Store exercises

    context = {
        'module': module,
        'exercises': exercises,  # ✅ Pass exercises to template
        'additional_resources': additional_resources,  # ✅ Pass additional resources to template
        'progress_value': 50  # ✅ Example progress value
    }
    
    return render(request, 'users/moduleOverview.html', context)



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

    return render(request, 'userModules.html', {"module_data": module_data})



def all_modules(request):
    modules = Module.objects.all()

    return render(request, 'all_modules.html', {'modules': modules})

@csrf_exempt
def rate_module(request, module_id):
    """Handles AJAX-based user rating for a module."""
    if request.method == "POST":
        module = get_object_or_404(Module, id=module_id)
        data = json.loads(request.body)
        rating_value = int(data.get("rating", 0))

        if 1 <= rating_value <= 5:
            # Save or update rating
            rating_obj, created = ModuleRating.objects.update_or_create(
                user=request.user.enduser,  # Ensure the user is logged in
                module=module,
                defaults={'rating': rating_value}
            )

            # Recalculate average rating
            average_rating = module.ratings.aggregate(Avg('rating'))['rating__avg']
            if average_rating:
                average_rating = round(average_rating, 1)

            return JsonResponse({"success": True, "average_rating": average_rating})

    return JsonResponse({"success": False, "message": "Invalid request"})