from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm
from django.contrib.auth.decorators import login_required
from .models import UserResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import User, EndUser
from client.models import Exercise, ExerciseQuestion

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


#A function for displaying a sign up page
def sign_up(request):
    """Sign up new users and create an EndUser profile automatically."""
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        profile_form = EndUserProfileForm(request.POST)

        if user_form.is_valid():
            # Save the User first
            user = user_form.save()

            # Ensure EndUser is created and linked
            enduser = EndUser.objects.create(user=user)

            # Save extra profile data (if applicable)
            profile_form = EndUserProfileForm(request.POST, instance=enduser)
            if profile_form.is_valid():
                profile_form.save()

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
def user_responses_main(request):
    """Shows all exercises as clickable boxes."""
    exercises = Exercise.objects.all()
    return render(request, "UserResponce/user_responses_main.html", {"exercises": exercises})


@login_required
def exercise_detail_view(request, exercise_id):
    """Shows all questions for a selected exercise, with all user responses."""
    
    exercise = get_object_or_404(Exercise, id=exercise_id)
    questions = exercise.questions.all()
    
    # Get the logged-in user’s profile
    enduser = getattr(request.user, 'User_profile', None)
    if not enduser:
        return redirect('dashboard')  

    # Fetch responses for each question in the exercise
    questions_with_responses = []
    for question in questions:
        responses = UserResponse.objects.filter(user=enduser, question=question)
        questions_with_responses.append({'question': question, 'responses': responses})

    return render(request, "UserResponce/exercise_detail.html", 
    {"exercise": exercise, "questions_with_responses": questions_with_responses})

