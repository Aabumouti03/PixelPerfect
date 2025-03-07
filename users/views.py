
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hashfrom 
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm, UserProfileForm
from django.contrib.auth import logoutfrom 
from .models import Program, Questionnaire, Question, QuestionResponse, Questionnaire_UserResponse,EndUser, UserModuleProgress, UserModuleEnrollment, UserProgramEnrollment
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib import messages
from client.models import Module, BackgroundStyle, Program, ProgramModule
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import os
import random
logger = logging.getLogger(__name__)

from django.conf import settings


# Create your views here.


def questionnaire(request):
    active_questionnaire = Questionnaire.objects.filter(is_active=True).first()

    if active_questionnaire:
        questions = Question.objects.filter(questionnaire=active_questionnaire)
        questions_data = [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type  # Add question type
            }
            for q in questions
        ]
    else:
        questions_data = []

    context = {
        "active_questionnaire": active_questionnaire,
        "questions_json": json.dumps(questions_data),
    }
    return render(request, "questionnaire.html", context)

@csrf_exempt
def submit_responses(request):
    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"success": False, "message": "User is not authenticated. Please log in."})

            data = json.loads(request.body)
            logger.info("Received data: %s", data)

            # ✅ Ensure the user exists
            try:
                user = EndUser.objects.get(user=request.user)
            except EndUser.DoesNotExist:
                return JsonResponse({"success": False, "message": "User not found. Please sign in."})

            # ✅ Ensure the questionnaire exists
            questionnaire_id = data.get("questionnaireId")
            if not questionnaire_id:
                return JsonResponse({"success": False, "message": "Questionnaire ID is missing."})

            try:
                questionnaire = Questionnaire.objects.get(id=questionnaire_id)
            except Questionnaire.DoesNotExist:
                return JsonResponse({"success": False, "message": "Questionnaire not found."})

            responses = data.get("responses", [])
            if not responses:
                return JsonResponse({"success": False, "message": "No responses provided."})

            # ✅ Ensure Questionnaire_UserResponse exists before adding responses
            questionnaire_user_response, created = Questionnaire_UserResponse.objects.get_or_create(
                user=user,
                questionnaire=questionnaire
            )

            for response in responses:
                question_id = response.get("questionId")
                value = response.get("value")

                if not question_id or value is None:
                    logger.error("Missing questionId or value in response: %s", response)
                    continue

                # ✅ Ensure the question exists
                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    logger.error("Question with ID %s does not exist.", question_id)
                    continue

                # ✅ Save the QuestionResponse
                question_response = QuestionResponse(
                    user_response=questionnaire_user_response,
                    question=question,
                    rating_value=int(value) if question.question_type in ["AGREEMENT", "RATING"] else None
                )

                try:
                    question_response.full_clean()  # Validate the model instance
                    question_response.save()
                except ValidationError as e:
                    logger.error("Validation error for question response: %s", str(e))
                    continue

            return JsonResponse({"success": True, "message": "Responses saved successfully!"})

        except Exception as e:
            logger.error("Error saving responses: %s", str(e))
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


@csrf_exempt
@login_required
def save_notes(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')

        # Get the EndUser instance for the logged-in user
        end_user = EndUser.objects.get(user=request.user)

        # Get or create the sticky note for the current user
        sticky_note, created = StickyNote.objects.get_or_create(user=end_user)
        sticky_note.content = content
        sticky_note.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_notes(request):
    try:
        # Get the EndUser instance for the logged-in user
        end_user = EndUser.objects.get(user=request.user)
        sticky_note = StickyNote.objects.get(user=end_user)
        return JsonResponse({'success': True, 'content': sticky_note.content})
    except StickyNote.DoesNotExist:
        return JsonResponse({'success': True, 'content': ''})  # Return empty content if no note exists


@login_required
def dashboard(request):
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    # Fetch the program the user is enrolled in (if any)
    user_program_enrollment = UserProgramEnrollment.objects.filter(user=end_user).first()
    program = user_program_enrollment.program if user_program_enrollment else None

    # Fetch program modules if the user is enrolled, sorted by order
    program_modules = program.program_modules.all().order_by("order") if program else []

    # Get user progress for each module
    user_progress = {
        progress.module.id: progress.completion_percentage
        for progress in UserModuleProgress.objects.filter(user=end_user)
    }

    # Mark only the first module as accessible
    previous_module_completed = True  # The first module is always accessible
    for program_module in program_modules:
        module = program_module.module
        module.progress_value = user_progress.get(module.id, 0)

        if previous_module_completed:
            module.is_unlocked = True  # Unlock if it's the first or previous is completed
        else:
            module.is_unlocked = False  # Keep locked

        previous_module_completed = module.progress_value == 100  # Update for next iteration

    # Get modules outside the program that the user is enrolled in
    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module', flat=True)
    outside_modules = Module.objects.filter(id__in=enrolled_modules).exclude(id__in=[pm.module.id for pm in program_modules])

    context = {
        'user': request.user,
        'program': program,
        'program_modules': program_modules,
        'outside_modules': outside_modules,  # Only enrolled modules outside the program
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def view_program(request, program_id):
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        return render(request, 'users/program_not_found.html')

    # Get the user's enrolled program
    user_program_enrollment = UserProgramEnrollment.objects.filter(user=end_user, program_id=program_id).first()
    
    if not user_program_enrollment:
        return render(request, 'users/program_not_found.html')

    program = user_program_enrollment.program
    program_modules = program.program_modules.all().order_by('order')  # Ensuring modules are in order

    # Fetch user progress for each module
    user_progress = {
        progress.module.id: progress.completion_percentage
        for progress in UserModuleProgress.objects.filter(user=end_user)
    }

    # Assign progress values and determine if a module is locked
    previous_completed = True  # First module should be unlocked
    for index, program_module in enumerate(program_modules):
        module = program_module.module
        module.progress_value = user_progress.get(module.id, 0)  # Default to 0%
        module.module_order = index + 1  # Assign order number

        # Lock modules that are not the first and depend on previous completion
        if previous_completed:
            module.locked = False
        else:
            module.locked = True

        # Update `previous_completed` for the next iteration
        previous_completed = module.progress_value == 100

    context = {
        'user': user,
        'program': program,
        'program_modules': program_modules,
    }
    
    return render(request, 'users/view_program.html', context)


#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'users/welcome_page.html')


def modules(request):
    return render(request, 'users/modules.html')

#edit back to users/profile.html later
def profile(request):
    return render(request, 'users/profile.html')

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
        if profile_form.is_valid():

            user_data = request.session.pop('user_form_data')
            user_form = UserSignUpForm(data=user_data)
            if user_form.is_valid():
                user = user_form.save()
                
                  # Added to autheticate user for questionnaire process
                authenticated_user = authenticate(username=user.username, password=user_data["password1"])
                if authenticated_user:
                    login(request, authenticated_user)

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect('welcome')

    else:
        profile_form = EndUserProfileForm()

    return render(request, "users/sign_up_step_2.html", {"profile_form": profile_form})


def log_out(request):
    """Handles logout only if the user confirms via modal."""
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
    user = request.user  # Get the logged-in user

    if request.method == "POST":
        try:
            # Delete the user account, which will cascade-delete related objects
            user.delete()
            logout(request)  # Log out after deletion
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('welcome_page')  # Redirect to a safe page after deletion

        except Exception as e:
            messages.error(request, f"An error occurred while deleting your account: {e}")
            return redirect('profile_page')  # Redirect back to the profile if deletion fails

    # Confirmation before deletion
    context = {'confirmation_text': "Are you sure you want to delete your account? This action cannot be undone."}
    return render(request, 'users/Profile/delete_account.html', context)


def module_overview(request, id):
    module = get_object_or_404(Module, id=id)

    try:
        end_user = EndUser.objects.get(user=request.user)
    except EndUser.DoesNotExist:
        return HttpResponse("EndUser profile does not exist. Please contact support.")

    progress = UserModuleProgress.objects.filter(module=module, user=end_user).first()
    progress_value = progress.completion_percentage if progress else 0

    return render(request, 'users/moduleOverview2.html', {'module': module, 'progress_value': progress_value})


@login_required
def user_modules(request):
    user = request.user
    end_user, created = EndUser.objects.get_or_create(user=user)

    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user)

    module_data = []

    for enrollment in enrolled_modules:
        module = enrollment.module
        progress = UserModuleProgress.objects.filter(user=end_user, module=module).first()

        progress_percentage = progress.completion_percentage if progress else 0
        background_style = module.background_style  # Get BackgroundStyle object

        module_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "progress": progress_percentage,
            "background_color": background_style.background_color if background_style else "#ffffff",
            "background_image": background_style.get_background_image_url() if background_style else "none",
        })

    return render(request, 'users/userModules.html', {"module_data": module_data})



def all_modules(request):
    modules = Module.objects.all()

    return render(request, 'all_modules.html', {'modules': modules})

