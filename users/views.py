from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import UserSignUpForm, LogInForm, EndUserProfileForm
from django.shortcuts import render, get_object_or_404

from .models import Module, UserModuleProgress, UserModuleEnrollment, EndUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
import os
from django.contrib import messages
from django.conf import settings
import random

from django.contrib.auth import get_user_model

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    """Welcome page view."""
    return render(request, 'users/welcome_page.html')


@login_required(login_url='log_in')
def dashboard(request):
    """Dashboard view, accessible only to logged-in users."""
    return render(request, 'users/dashboard.html')

def modules(request):
    return render(request, 'users/modules.html')

def profile(request):
    return render(request, 'users/profile.html')

def welcome_page(request):
    return render(request, 'users/welcome_page.html')

def about(request):
    return render(request, 'users/about.html')

def contact_us(request):
    return render(request, 'users/contact_us.html')

ADMIN_USERNAME = "SuperUser"


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

                if user.username == ADMIN_USERNAME and user.is_superuser:
                    return redirect('client_dashboard')

                return redirect('dashboard')

    else:
        form = LogInForm()

    return render(request, "users/log_in.html", {"form": form})


def sign_up_step_1(request):
    """Handles Step 1: User Account Details"""
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        if user_form.is_valid():
            request.session["user_form_data"] = user_form.cleaned_data
            return redirect("sign_up_step_2")


    else:
        user_form_data = request.session.get("user_form_data", {})
        user_form = UserSignUpForm(initial=user_form_data)

    return render(request, "users/sign_up_step_1.html", {"user_form": user_form})

def sign_up_step_2(request):
    """Handles Step 2: Profile Details"""
    user_data = request.session.get("user_form_data")

    
    if not user_data:
        return redirect("sign_up_step_1")

   
    user_form = UserSignUpForm(data=user_data)
    if not user_form.is_valid():
        return redirect("sign_up_step_1")

    if request.method == "POST":
        profile_form = EndUserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            del request.session["user_form_data"]
            return redirect("log_in")


    else:
        profile_form = EndUserProfileForm()

    return render(request, "users/sign_up_step_2.html", {"profile_form": profile_form})


def log_out(request):
    """Handles logout only if the user confirms via modal."""
    if request.method == "POST":
        logout(request)
        return redirect('log_in')


    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))  


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

