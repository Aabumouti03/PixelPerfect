from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignUpForm
from django.shortcuts import render, get_object_or_404
from .models import Module, UserModuleProgress, UserModuleEnrollment, EndUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login 
from django.contrib.auth.models import User  
import os
from django.conf import settings
import random

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'welcome_page.html')

# Login view for the user
def log_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user) 
                return redirect('dashboard')  
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'log_in.html', {'form': form})

#A function for displaying a sign up page
def sign_up(request):
    form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')

def logout_view(request):
    return render(request, 'logout.html')

def module_overview(request, id):
    module = get_object_or_404(Module, id=id)

    try:
        end_user = EndUser.objects.get(user=request.user)
    except EndUser.DoesNotExist:
        return HttpResponse("EndUser profile does not exist. Please contact support.")

    progress = UserModuleProgress.objects.filter(module=module, user=end_user).first()
    progress_value = progress.completion_percentage if progress else 0

    return render(request, 'moduleOverview2.html', {'module': module, 'progress_value': progress_value})


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

def all_modules(request):
    #modules = Module.objects.all()
    
    all_modules = [
        {"title": "Mindfulness for a Balanced Life", "description": "Explore meditation, breathing exercises, and mental relaxation techniques to improve overall well-being.", "progress": 25},
        {"title": "Workplace Safety & Adaptation", "description": "Covers health protocols, ergonomic setups, and adjustments to the work environment.", "progress": 82},
        {"title": "Effective Communication & Collaboration", "description": "Focuses on rebuilding teamwork, trust, and clear workplace communication.", "progress": 9},
        {"title": "Time Management & Productivity", "description": "Provides strategies for balancing tasks, avoiding burnout, and staying efficient.", "progress": 47},
        {"title": "Leadership & Emotional Intelligence", "description": "Develop leadership skills, empathy, and team motivation strategies.", "progress": 64},
        {"title": "Remote Work Best Practices", "description": "Learn how to stay productive while working remotely.", "progress": 38},
        {"title": "Mental Health & Workplace Well-being", "description": "Gain awareness of workplace mental health and stress management techniques.", "progress": 55},
        {"title": "Breaking the Stigma: Mental Health Awareness", "description": "A module focusing on reducing workplace stigma around mental health.", "progress": 15},
    ]
    return render(request, 'all_modules.html', {"all_modules": all_modules})

