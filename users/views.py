from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm
from django.contrib.auth.decorators import login_required
from .models import UserResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import User, EndUser, Module
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

def about(request):
    return render(request, 'about.html')

def contact_us(request):
    return render(request, 'contact_us.html')

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

    return render(request, 'sign_up_step_1.html', {'user_form': user_form})

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

    return render(request, 'sign_up_step_2.html', {'profile_form': profile_form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

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

