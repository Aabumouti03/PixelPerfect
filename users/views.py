from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSignUpForm, LogInForm, EndUserProfileForm
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
    return render(request, 'users/welcome_page.html')

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
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/log_in.html', {'form': form})

def dashboard(request):
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