import os
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404

from client.models import Program  
from .forms import EndUserProfileForm, LogInForm, UserProfileForm, UserSignUpForm
from .models import EndUser, Module, UserModuleEnrollment, UserModuleProgress, UserProgramEnrollment


# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'users/welcome_page.html')

def dashboard(request):
    return render(request, 'users/dashboard.html')

def modules(request):
    return render(request, 'users/modules.html')

#edit back to users/profile.html later
def profile(request):
    return render(request, 'users/profile.html')

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
def show_profile(request):
    """View to display the user profile"""
    user = request.user

    if hasattr(user, 'User_profile'):
        return render(request, 'users/Profile/show_profile.html', {'user': user})
    else:
        messages.error(request, "User profile not found.")
        return redirect('welcome_page')

 
@login_required  
def update_profile(request):
    """Update user profile details."""
    user = request.user  

    if not hasattr(user, 'User_profile'):
        messages.error(request, "Profile not found.")
        return redirect('welcome_page')

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user.User_profile, user=user)
        if form.is_valid():
            form.save()
            
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                print("Updating password for user:", user.username)  # Debugging
                user.set_password(new_password)
                user.save()
                print("Password updated successfully!")  # Debugging
                update_session_auth_hash(request, user)

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('show_profile')

        else:
            print("Form is invalid! Errors:", form.errors)  # Debugging
 
    else:
        form = UserProfileForm(instance=user.User_profile, user=user)

    return render(request, 'users/Profile/update_profile.html', {'form': form, 'user': user})



@login_required
def delete_account(request):
    """Handle both confirmation page and actual account deletion."""
    if request.method == "POST":
        user = request.user

        # Delete all related objects first
        user.User_profile.program_enrollments.all().delete()
        user.User_profile.module_enrollments.all().delete()
        user.User_profile.program_progress.all().delete()
        user.User_profile.module_progress.all().delete()

        # Delete EndUser profile first, if it exists
        end_user_profile = getattr(user, 'User_profile', None)
        if end_user_profile:
            end_user_profile.delete()
        
        # Then delete user and log them out
        user.delete()
        logout(request)
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('welcome_page')

    context = {'confirmation_text': "Are you sure you want to delete your account? This action cannot be undone."}
    return render(request, 'users/Profile/delete_account.html', context)


@login_required
def recommended_programs(request):
    """Displays programs for users to enroll in."""
    user = request.user
    available_programs = Program.objects.all()  # Later replace with recommended logic
    #available_programs = Program.objects.filter(recommended_for=user)  # Adjust based on actual recommendation logic

    if request.method == "POST":
        selected_program_id = request.POST.get("program_id")

        if selected_program_id:
            try:
                program = Program.objects.get(id=selected_program_id)
                UserProgramEnrollment.objects.update_or_create(
                    user=user, defaults={"program": program}
                )
                return redirect("dashboard")
            except ObjectDoesNotExist:
                pass  # If program doesn't exist, do nothing (or handle error message)

        elif "skip" in request.POST:
            UserProgramEnrollment.objects.update_or_create(
                user=user, defaults={"program": None}
            )
            return redirect("dashboard")

    return render(request, "users/recommended_programs.html", {"programs": available_programs or []})  # Ensure programs is always a list



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
