from django.shortcuts import render
from django.http import HttpResponse
from .forms import SignUpForm

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'welcome_page.html')

#A function for displaying a log in page
def log_in(request):
    return render(request, 'log_in.html')

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
    progress = 50  # This could come from your database or other source based on the `id`
    return render(request, 'moduleOverview2.html', {'progress_value': progress})


def user_modules(request):
    modules = [
        {"id": 1, "title": "Mindfulness for a Balanced Life", "description": "Explore meditation, breathing exercises, and mental relaxation techniques to improve overall well-being.", "progress": 25},
        {"id": 2, "title": "Workplace Safety & Adaptation", "description": "Covers health protocols, ergonomic setups, and adjustments to the work environment.", "progress": 82},
        {"id": 3, "title": "Effective Communication & Collaboration", "description": "Focuses on rebuilding teamwork, trust, and clear workplace communication.", "progress": 9},
        {"id": 4, "title": "Time Management & Productivity", "description": "Provides strategies for balancing tasks, avoiding burnout, and staying efficient.", "progress": 47},
    ]
    return render(request, 'userModules.html', {"module_data": modules})
