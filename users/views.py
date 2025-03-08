from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import StickyNote, EndUser, Program
import json
from .models import Module, UserModuleProgress, UserModuleEnrollment, EndUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.models import User  

import os
import json
import random
import logging
from django.urls import reverse
from django.db.models import Avg
from django.contrib import messages
from django.forms import ValidationError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from users.helpers_modules import calculate_progress
from django.contrib.auth.decorators import login_required 
from client.models import Category, Program,ModuleRating,Exercise
from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm, UserProfileForm, ExerciseAnswerForm
from .models import Program, Questionnaire,EndUser, Question, QuestionResponse, Questionnaire_UserResponse,EndUser, StickyNote, UserModuleProgress, UserModuleEnrollment, UserProgramEnrollment, Program, Module
logger = logging.getLogger(__name__)
from collections import defaultdict


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



from .forms import LogInForm, EndUserProfileForm, UserSignUpForm
from django.shortcuts import render, get_object_or_404
from client.models import Program
from users.models import UserProgramEnrollment, EndUser, JournalEntry
from django.utils.timezone import now
from datetime import datetime, timedelta



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
    
from django.shortcuts import render, get_object_or_404
from .models import Program, Module, UserProgramEnrollment, UserModuleProgress, EndUser


from django.shortcuts import render
from .models import Program, Module, UserProgramEnrollment, UserModuleProgress, UserModuleEnrollment, EndUser
from django.shortcuts import render, get_object_or_404
from client.models import Program, ProgramModule
from users.models import UserProgramEnrollment, EndUser


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
        'user': user,
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
    '''A function for displaying a page that welcomes users'''
    return render(request, 'users/welcome_page.html')


def modules(request):
    return render(request, 'users/modules.html')

#edit back to users/profile.html later
def profile(request):
    return render(request, 'users/profile.html')
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


        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password1"])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            del request.session["user_form_data"]
            return redirect("log_in")


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


@login_required
def recommended_programs(request):
    """Displays programs for users to enroll in and handles AJAX enrollment updates."""
    user = request.user
    enrolled_programs = Program.objects.filter(enrolled_users__user=user.User_profile)

    end_user = EndUser.objects.get(user=user)

    # Get the dictionary of programs categorized by category
    categorized_programs = assess_user_responses_programs(end_user)

    # Flatten the dictionary values (lists of programs) into a single list
    all_programs = [program for program_list in categorized_programs.values() for program in program_list]


    if request.method == "POST":
        try:
            data = json.loads(request.body)
            program_id = data.get("program_id")
            action = data.get("action")

            program = Program.objects.get(id=program_id)
            user_profile = user.User_profile

            # Unenroll the user from all programs before enrolling in the new one
            if action == "enroll":
                # Remove enrollment from any previously enrolled program
                UserProgramEnrollment.objects.filter(user=user_profile).delete()
                UserProgramEnrollment.objects.create(user=user_profile, program=program)

            elif action == "unenroll":
                UserProgramEnrollment.objects.filter(user=user_profile, program=program).delete()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return render(request, "users/PersonalizedPlan/recommended_programs.html", {
        "programs": all_programs or [],
        "enrolled_programs": enrolled_programs
    })


@login_required
def recommended_modules(request):
    """Displays modules for users to enroll in and handles AJAX enrollment updates."""
    user = request.user
    enrolled_modules = Module.objects.filter(enrolled_users__user=user.User_profile)

    end_user = EndUser.objects.get(user=user)

    # Get the dictionary of modules categorized by category
    categorized_modules = assess_user_responses_modules(end_user)

    # Flatten the dictionary values (lists of modules) into a single list
    all_modules = [module for module_list in categorized_modules.values() for module in module_list]


    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Read AJAX request body
            module_id = data.get("module_id")
            action = data.get("action")

            module = Module.objects.get(id=module_id)
            user_profile = user.User_profile

            if action == "enroll":
                UserModuleEnrollment.objects.get_or_create(user=user_profile, module=module)
            elif action == "unenroll":
                UserModuleEnrollment.objects.filter(user=user_profile, module=module).delete()

            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return render(request, "users/PersonalizedPlan/recommended_modules.html", {
        "modules": all_modules or [],
        "enrolled_modules": enrolled_modules
    })

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

@login_required
def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises and additional resources."""
    
    
    module = get_object_or_404(Module, id=module_id)

    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    
    exercises = []
    additional_resources = list(module.additional_resources.all())

    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())


    completed_items = 0
    total_items = len(exercises) + len(additional_resources)


    for exercise in exercises:
        if exercise.status=='completed':
            completed_items += 1

    for resource in additional_resources:
        if resource.status=='completed':
            completed_items += 1

    progress_value = 0
    if total_items > 0:
        progress_value = (completed_items / total_items) * 100

    user_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
    user_progress.completion_percentage = progress_value
    user_progress.save()

    context = {
        'module': module,
        'exercises': exercises,
        'additional_resources': additional_resources,
        'progress_value': progress_value,  
    }

    return render(request, 'users/moduleOverview.html', context)

@login_required
def exercise_detail(request, exercise_id):
    """Fetch the exercise details, including questions, saved responses, and the related diagram."""

    exercise = get_object_or_404(Exercise, id=exercise_id)

    user, created = EndUser.objects.get_or_create(user=request.user)

    diagram = None
    for section in exercise.sections.all():
        if section.diagram:  
            diagram = section.diagram  
            break  

    if request.method == 'POST':
        for question in exercise.questions.all():
            answer_text = request.POST.get(f'answer_{question.id}', '').strip()


        return redirect('exercise_detail', exercise_id=exercise.id)

    return render(request, 'users/exercise_detail.html', {
        'exercise': exercise,
        'diagram': diagram, 
    })

@csrf_exempt  
def rate_module(request, module_id):
    """Handles AJAX-based user rating for a module."""
    if request.method == "POST" and request.user.is_authenticated:
        module = get_object_or_404(Module, id=module_id)
        try:
            data = json.loads(request.body)
            rating_value = int(data.get("rating", 0))

            if 1 <= rating_value <= 5:
             
                end_user = request.user.User_profile 

                rating_obj, created = ModuleRating.objects.update_or_create(
                    user=end_user,  
                    module=module,
                    defaults={'rating': rating_value}
                )

                average_rating = module.ratings.aggregate(Avg('rating'))['rating__avg']
                average_rating = round(average_rating, 1) if average_rating else 0

                return JsonResponse({"success": True, "average_rating": average_rating})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"})

    return JsonResponse({"success": False, "message": "Invalid request or unauthorized user"})

@login_required
def mark_done(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("id")
        item_type = data.get("type")
        action = data.get("action")  # 'done' or 'undo'

        user = request.user
        end_user = EndUser.objects.get(user=user)  

        if item_type == "resource":
            resource = AdditionalResource.objects.get(id=item_id)
            if resource.status == 'completed':
                resource.status = 'in_progress'
            else:
                resource.status = 'completed'
            resource.save()
            module = Module.objects.filter(additional_resources=resource).first()

        elif item_type == "exercise":
            exercise = Exercise.objects.get(id=item_id)
            if exercise.status == 'completed':
                exercise.status = 'in_progress'
            else:
                exercise.status = 'completed'
            exercise.save()
            module = exercise.sections.first().modules.first()

     
        user_module_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
        user_module_progress.completion_percentage = calculate_progress(end_user, module)
        user_module_progress.save()

        return JsonResponse({
            "success": True,
            "updated_progress": user_module_progress.completion_percentage
        })

    return JsonResponse({"success": False})


def all_modules(request):
    modules = Module.objects.all()
    return render(request, 'users/all_modules.html', {'modules': modules})

@login_required
def welcome_view(request):
    return render(request, 'users/welcome.html')

@login_required
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
    return render(request, "users/questionnaire.html", context)

@csrf_exempt
@login_required
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

            # Create a new Questionnaire_UserResponse 
            questionnaire_user_response = Questionnaire_UserResponse.objects.create(
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

            
            return JsonResponse({"success": True, "redirect_url": reverse("recommended_programs")})
        
        except Exception as e:
            logger.error("Error saving responses: %s", str(e))
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})

def assess_user_responses_programs(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests programs based on negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested programs.
    """

    # Step 1: Get the latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()

    if not latest_response:
        return {}  # No responses, return empty recommendations

    # Step 2: Fetch all responses from the latest questionnaire submission
    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    # Step 3: Reset category scores for this new response
    category_scores = defaultdict(int)

    # Step 4: Calculate scores for each category
    for response in user_responses:
        question = response.question  # Get the related question
        category = question.category  # Get the category

        if category:  # Ensure question has a category
            adjusted_score = response.rating_value * question.sentiment  # Multiply response by sentiment
            category_scores[category.id] += adjusted_score  # Update category score

    # Step 5: Find categories with negative scores
    low_score_categories = [category_id for category_id, score in category_scores.items() if score < 0]

    # Step 6: Fetch programs from the negatively scored categories
    suggested_programs = {}
    for category_id in low_score_categories:
        category = get_object_or_404(Category, id=category_id)
        programs = Program.objects.filter(categories=category)  
        suggested_programs[category.name] = list(programs)  # Convert queryset to list

    return suggested_programs

def assess_user_responses_modules(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests programs based on negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested programs.
    """

    # Step 1: Get the latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()

    if not latest_response:
        return {}  # No responses, return empty recommendations

    # Step 2: Fetch all responses from the latest questionnaire submission
    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    # Step 3: Reset category scores for this new response
    category_scores = defaultdict(int)

    # Step 4: Calculate scores for each category
    for response in user_responses:
        question = response.question  # Get the related question
        category = question.category  # Get the category

        if category:  # Ensure question has a category
            adjusted_score = response.rating_value * question.sentiment  # Multiply response by sentiment
            category_scores[category.id] += adjusted_score  # Update category score

    # Step 5: Find categories with negative scores
    low_score_categories = [category_id for category_id, score in category_scores.items() if score < 0]

    # Step 6: Fetch programs from the negatively scored categories
    suggested_modules = {}
    for category_id in low_score_categories:
        category = get_object_or_404(Category, id=category_id)
        modules = Module.objects.filter(categories=category)  
        suggested_modules[category.name] = list(modules)  # Convert queryset to list

    return suggested_modules