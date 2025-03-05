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
import json
from django.http import JsonResponse
from django.conf import settings
import random
from client.models import Module 

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


def log_out(request):
    """Confirm logout. If confirmed, redirect to welcome page. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('welcome_page')

    # if user cancels, stay on the same page
    return render(request, 'dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})
def logout_view(request):
    return render(request, 'logout.html')

# def module_overview(request, id):
#     module = get_object_or_404(Module, id=id)

#     try:
#         end_user = EndUser.objects.get(user=request.user)
#     except EndUser.DoesNotExist:
#         return HttpResponse("EndUser profile does not exist. Please contact support.")

#     progress = UserModuleProgress.objects.filter(module=module, user=end_user).first()
#     progress_value = progress.completion_percentage if progress else 0

#     return render(request, 'moduleOverview2.html', {'module': module, 'progress_value': progress_value})

def module_overview(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "users/moduleOverview.html", {"module": module})


@login_required
def unenroll_module(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Unenroll Request Received:", data)  # ✅ Debugging

            module_title = data.get("title")

            # Find the module
            module = Module.objects.filter(title=module_title).first()
            if not module:
                print("Error: Module not found")
                return JsonResponse({"success": False, "error": "Module not found"}, status=404)

            user = request.user
            try:
                end_user = EndUser.objects.get(user=user)
            except EndUser.DoesNotExist:
                print("Error: User not found")
                return JsonResponse({"success": False, "error": "User not found"}, status=400)

            # Check if the user is enrolled
            enrollment = UserModuleEnrollment.objects.filter(user=end_user, module=module)
            if not enrollment.exists():
                print("Error: User is NOT enrolled")  # ✅ Debugging
                return JsonResponse({"success": False, "error": "Not enrolled"}, status=400)

            # Delete the enrollment
            enrollment.delete()
            print("Success: User unenrolled")  # ✅ Debugging

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            print("Error: Invalid JSON")
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    print("Error: Invalid request method")
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def enroll_module(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received Data:", data)  # ✅ Debugging

            module_title = data.get("title")
            if not module_title:
                print("Error: Missing module title")  # ✅ Debugging
                return JsonResponse({"success": False, "error": "Missing module title"}, status=400)

            # Check if the module exists
            module = Module.objects.filter(title=module_title).first()
            if not module:
                print("Error: Module not found")  # ✅ Debugging
                return JsonResponse({"success": False, "error": "Module not found"}, status=404)

            user = request.user
            end_user, created = EndUser.objects.get_or_create(user=user)

            # Check if the user is already enrolled
            if UserModuleEnrollment.objects.filter(user=end_user, module=module).exists():
                print("Error: Already enrolled")  # ✅ Debugging
                return JsonResponse({"success": False, "error": "Already enrolled"}, status=400)

            # Enroll the user
            UserModuleEnrollment.objects.create(user=end_user, module=module)
            print("Success: User enrolled in module!")  # ✅ Debugging

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            print("Error: Invalid JSON")  # ✅ Debugging
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    print("Error: Invalid request method")  # ✅ Debugging
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def user_modules(request):
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    # Fetch enrolled modules
    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).select_related('module')

    module_data = []
    for enrollment in enrolled_modules:
        module = enrollment.module
        progress = UserModuleProgress.objects.filter(user=end_user, module=module).first()
        progress_percentage = progress.completion_percentage if progress else 0

        module_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "progress": progress_percentage,
            "background_image": f'img/backgrounds/{module.id}.jpg'  # Change based on actual background path
        })

    return render(request, 'userModules.html', {"module_data": module_data})


@login_required
def all_modules(request):
    modules = Module.objects.all()  # Fetch all modules
    user = request.user

    # Get the current user's enrolled modules
    try:
        end_user = EndUser.objects.get(user=user)
        enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module__title', flat=True)
    except EndUser.DoesNotExist:
        enrolled_modules = []

    return render(request, 'all_modules.html', {
        'all_modules': modules,
        'enrolled_modules': list(enrolled_modules)  # Convert QuerySet to list
    })