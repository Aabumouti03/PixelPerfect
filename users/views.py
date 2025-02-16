<<<<<<< HEAD
from django.shortcuts import render, redirect  
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import ExerciseResponse
from client.models import Exercise
from django.views.decorators.csrf import csrf_protect  # ✅ Add this line
=======
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm
>>>>>>> origin/userAuthentication

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def profile(request):
    return render(request, 'profile.html')

<<<<<<< HEAD
def logout_view(request):
    return render(request, 'logout.html')

# @csrf_protect  # Ensure CSRF protection is applied properly
# def custom_login_view(request):
#     """Handles user login and redirects correctly."""
    
#     if request.user.is_authenticated:
#         return redirect('dashboard')  # 🔄 Redirect already logged-in users to dashboard

#     if request.method == "POST":
#         form = AuthenticationForm(data=request.POST)

#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)

#             # Get the next page, default to dashboard
#             next_url = request.POST.get('next', 'dashboard')

#             # Avoid redirecting to login again
#             if next_url == request.path:
#                 next_url = 'dashboard'  
                
#             return redirect(next_url)

#     else:
#         form = AuthenticationForm()
    
#     return render(request, 'users/login.html', {'form': form})


# @login_required
# def user_responses_view(request):
#     """Show responses only for the logged-in user."""
    
#     # ✅ Check if the user has an `EndUser` profile
#     if not hasattr(request.user, 'enduser'):
#         return redirect('dashboard')  # Redirect instead of login loop

#     user = request.user.enduser  
#     exercises = Exercise.objects.prefetch_related("questions").all()

#     responses_by_exercise = {
#         exercise: ExerciseResponse.objects.filter(user=user, question__in=exercise.questions.all())
#         for exercise in exercises
#     }

#     return render(request, 'users/user_responses.html', {'responses_by_exercise': responses_by_exercise})

# def logout_view(request):
#     """Logs the user out and redirects to login."""
#     logout(request)
#     return render(request, 'users/logged_out.html') 
=======
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
>>>>>>> origin/userAuthentication
