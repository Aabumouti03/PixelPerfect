from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm
from django.contrib.auth.decorators import login_required
from .models import UserResponse
from client.models import Exercise
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import User, EndUser
# Create your views here.

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


def sign_up(request):
    """Sign up new users and create an EndUser profile automatically."""
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        profile_form = EndUserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Save the User first
            user = user_form.save()

            # Ensure EndUser is created and linked
            enduser = profile_form.save(commit=False)  # Create but don't save yet
            enduser.user = user  # Associate with user
            enduser.save()  # Now save to DB

            # Log the user in after sign-up
            login(request, user)
            return redirect('dashboard')  # Redirect to dashboard after sign-up

    else:
        user_form = UserSignUpForm()
        profile_form = EndUserProfileForm()

    return render(request, 'sign_up.html', {'user_form': user_form, 'profile_form': profile_form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to welcome page. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('welcome_page')

    # if user cancels, stay on the same page
    return render(request, 'dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})


@login_required
def user_responses_view(request):
    """Show responses grouped by exercise for the logged-in user."""
    
    enduser = getattr(request.user, 'User_profile', None)   
    if not enduser:
        return redirect('dashboard') 
    
    exercises = Exercise.objects.prefetch_related("questions").all()
    responses_by_exercise = {}

    for exercise in exercises:
        questions = exercise.questions.all()
        responses = UserResponse.objects.filter(user=enduser, question__in=questions)  
        responses_by_exercise[exercise] = responses

    return render(request, 'user_responses.html', {'responses_by_exercise': responses_by_exercise})  
