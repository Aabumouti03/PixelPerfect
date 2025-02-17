from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import EndUserProfileForm, UserSignUpForm, EndUserProfileForm, LogInForm

# Create your views here.

@login_required 
def profile(request):
    """View to display the user profile"""
    user = request.user

    if hasattr(user, 'User_profile'):  # Check if profile exists
        return render(request, 'Profile/show_profile.html', {'user': user.User_profile})
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
        form = EndUserProfileForm(request.POST, instance=user.User_profile, user=user)
        if form.is_valid():
            try:
                form.save()
            except Exception:
                form.add_error(None, "An unexpected error occurred. Please try again.")
            else:
                messages.success(request, "Your profile has been updated successfully!")
                return redirect('show_profile')  
    else:
        form = EndUserProfileForm(instance=user.User_profile, user=user)

    return render(request, 'Profile/update_profile.html', {'form': form, 'user': user})



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
    return render(request, 'Profile/delete_account.html', context)



def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')

def welcome_page(request):
    return render(request, 'welcome_page.html')

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

    return render(request, 'log_in.html', {'form': form})


#A function for displaying a sign up page
def sign_up(request):
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        profile_form = EndUserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('log_in')

    else:
        user_form = UserSignUpForm()
        profile_form = EndUserProfileForm()

    return render(request, 'sign_up.html', {'user_form': user_form, 'profile_form': profile_form})

from django.shortcuts import render, redirect
from django.contrib.auth import logout

def log_out(request):
    """Confirm logout. If confirmed, redirect to welcome page. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('welcome_page')

    # if user cancels, stay on the same page
    return render(request, 'dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})
