import os
import json
import random
import logging
from django.conf import settings
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db.models import Avg
from .models import JournalEntry, User
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from users.helpers_modules import calculate_progress, update_user_program_progress
from django.contrib.auth.decorators import login_required 
from client.models import Category, Program,ModuleRating,Exercise
from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout, update_session_auth_hash
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm, UserProfileForm, ExerciseAnswerForm
from .models import Program, Questionnaire,EndUser, Question, QuestionResponse, Questionnaire_UserResponse,EndUser, StickyNote, UserModuleProgress, UserModuleEnrollment, UserProgramEnrollment, Program, Module, Quote
logger = logging.getLogger(__name__)
from .utils import send_verification_email_after_sign_up 
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from users.models import (
    EndUser, StickyNote, UserModuleProgress, UserModuleEnrollment,
    UserProgramEnrollment, JournalEntry,  UserExerciseProgress, UserResourceProgress,UserVideoProgress
)
from client.models import (
    Program, Module, ProgramModule, ModuleRating, Exercise, Category,
    AdditionalResource, Exercise,VideoResource
)
from users.models import (
    Questionnaire, Question, QuestionResponse, Questionnaire_UserResponse
)
from .helpers_questionnaire import assess_user_responses_modules, assess_user_responses_programs

# Logger setup
logger = logging.getLogger(__name__)




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

@csrf_protect
@login_required
def submit_responses(request):
    if request.method == "POST":
        try:
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
            redirect('recommended_programs')
            return JsonResponse({"success": True, "message": "Responses saved successfully!"})

        except Exception as e:
            logger.error("Error saving responses: %s", str(e))
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})

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
    unlocked_modules = set()

    for program_module in program_modules:
        module = program_module.module
        module.progress_value = user_progress.get(module.id, 0)

        if previous_module_completed:
            module.is_unlocked = True  # Unlock if it's the first or previous is completed
            unlocked_modules.add(module.id)  # Store unlocked module IDs
        else:
            module.is_unlocked = False  # Keep locked

        previous_module_completed = module.progress_value == 100  # Update for next iteration

    # Get modules outside the program that the user is enrolled in (standalone modules are always unlocked)
    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module', flat=True)
    outside_modules = Module.objects.filter(id__in=enrolled_modules).exclude(id__in=[pm.module.id for pm in program_modules])

    # Get recently accessed modules **EXCLUDING LOCKED ONES**
    recent_enrollments = UserModuleEnrollment.objects.filter(user=end_user).order_by('-last_accessed')[:3]

    # Ensure only unlocked modules appear in recently accessed
    recent_modules = [
        enrollment.module for enrollment in recent_enrollments
        if enrollment.module.id and (
            enrollment.module.id in unlocked_modules or  # Module is unlocked in a program
            enrollment.module in outside_modules  # Standalone modules are always unlocked
        )
    ]

    quote_of_the_day = Quote.get_quote_of_the_day()
    
    context = {
        'user': request.user,
        'program': program,
        'program_modules': program_modules,
        'outside_modules': outside_modules,  # Only enrolled modules outside the program
        'recent_modules': recent_modules,  # Excludes locked modules
        "quote_of_the_day": quote_of_the_day
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


def welcome_page(request):
    '''A function for displaying a page that welcomes users'''
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

def log_in(request):
    """Log in page view function"""

    error_message = None
    if request.method == "POST":
        form = LogInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').strip()  # Trim spaces
            password = form.cleaned_data.get('password').strip()

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.email_verified:
                    error_message = "You must verify your email before logging in."
                else:
                    login(request, user)

                    # Redirect to `next` if available
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)

                    # Superuser goes to `client_dashboard`
                    if user.is_superuser:
                        return redirect('client_dashboard')

                    # Regular users go to `dashboard`
                    return redirect('dashboard')

    else:
        form = LogInForm()

    return render(request, "users/log_in.html", {"form": form, "error_message": error_message})

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
    """Handles Step 2: Profile Details and Email Verification."""
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
            user.email_verified = False
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            del request.session["user_form_data"]

            send_verification_email_after_sign_up(user, request)

            return render(request, "users/sign_up_email_verification.html") #modify the html for this (extend the welcome page navbar in it and then write something relayted to like we sent a verification link to your email.)
    else:
        profile_form = EndUserProfileForm()

    return render(request, "users/sign_up_step_2.html", {"profile_form": profile_form})

def sign_up_email_verification(request):
    return render(request, "users/sign_up_email_verification.html")

def verify_email_after_sign_up(request, uidb64, token):
    """Verify the user's email after signing up."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return HttpResponse("Invalid verification link.") #change this to a new html that displays the same message and extend the welcome page navbar.

    if default_token_generator.check_token(user, token):
        user.email_verified = True  
        user.save()
        return redirect('verification_done')

    return HttpResponse("Invalid or expired token.")

def verification_done(request):
    return render(request, "users/verification_done.html")

def get_started(request):
    return render(request, "users/get_started.html")

@login_required
def log_out(request):
    """Handles logout only if the user confirms via modal."""
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

    referer_url = request.META.get('HTTP_REFERER')
    if referer_url:
        return redirect(referer_url)
    
    return redirect('dashboard')

@login_required 
def show_profile(request):
    """View to display the user profile"""
    user = request.user

    # Check if the session variable exists
    if 'profile_update_popup' in request.session:
        # If the session variable is set, show the pop-up message
        profile_update_popup = request.session['profile_update_popup']

        # Remove the session variable after showing the message
        del request.session['profile_update_popup']
    else:
        profile_update_popup = None

    if hasattr(user, 'User_profile'):
        return render(request, 'users/Profile/show_profile.html', {'user': user, 'profile_update_popup': profile_update_popup})
    else:
        messages.error(request, "User profile not found.")
        return redirect('welcome_page')

 
@login_required  
def update_profile(request):
    """Update user profile details, including email verification."""
    user = request.user  

    if not hasattr(user, 'User_profile'):
        messages.error(request, "Profile not found.")
        return redirect('welcome_page')

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user.User_profile, user=user)
        if form.is_valid():
            form.save()
            user.User_profile.save()  #  Explicitly save the profile
            user.refresh_from_db()  #  Ensure data in tests matches DB state

            # Handle email change verification
            new_email = form.cleaned_data.get("new_email")
            if new_email:
                new_email = new_email.strip().lower()  # Convert to lowercase
                
                # Only proceed if the email has actually changed
                if new_email != user.email.lower():  # Ensure case-insensitive comparison
                    # Save the new email for verification
                    user.new_email = new_email
                    user.save()

                    # Generate email verification token
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)

                    # Create verification link
                    verification_link = request.build_absolute_uri(f"/verify-email/{uid}/{token}/")

                    # Send verification email
                    send_mail_status = send_mail(
                        "Confirm Your Email Change",
                        f"Click the link to confirm your email change: {verification_link}",
                        "noreply@example.com",
                        [new_email],
                        fail_silently=False,
                    )

                    request.session['profile_update_popup'] = 'verification_sent'
                    request.session.save()  # Ensure session data is persisted before redirecting
                else:
                    # If the email hasn't changed, just don't do anything with the email
                    user.new_email = None
                    user.save()

            # Handle password update
            new_password = form.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)


            return redirect('show_profile')

        else:
            messages.error(request, "There were errors in the form.")

    else:
        form = UserProfileForm(instance=user.User_profile, user=user)

    return render(request, 'users/Profile/update_profile.html', {'form': form, 'user': user})


def verify_email(request, uidb64, token):
    User = get_user_model()
    
    try:
        # Decode user id
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return HttpResponse("Invalid verification link.")
    
    # Check token validity
    if default_token_generator.check_token(user, token):
        if user.new_email:  # Ensure there's a new email to set
            user.email = user.new_email 
            user.new_email = None  
            user.email_verified = True  
            user.save()
            
            request.session['profile_update_popup'] = 'profile_updated'
            return redirect('log_in')

    return HttpResponse("Invalid or expired token.")


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
            return redirect('show_profile')  # Redirect back to the profile if deletion fails

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
        })

    return render(request, 'users/userModules.html', {"module_data": module_data})

@login_required
def module_overview(request, module_id):
    """Fetch the module by ID and retrieve related exercises, additional resources, and videos for a specific user.""" 
    
    module = get_object_or_404(Module, id=module_id)
    user = request.user

    # Ensure the EndUser profile exists
    end_user, created = EndUser.objects.get_or_create(user=user)

    # Fetch exercises, additional resources, and videos linked to the module
    exercises = []
    for section in module.sections.all():
        if section.exercises.exists():
            exercises.extend(section.exercises.all())
    additional_resources = list(module.additional_resources.all())
    video_resources = list(module.video_resources.all()) 

    user_exercise_progress = {
        progress.exercise.id: progress.status for progress in UserExerciseProgress.objects.filter(user=end_user, exercise__in=exercises)
    }

    user_resource_progress = {
        progress.resource.id: progress.status for progress in UserResourceProgress.objects.filter(user=end_user, resource__in=additional_resources)
    }

    user_video_progress = {
        progress.video.id: progress.status for progress in UserVideoProgress.objects.filter(user=end_user, video__in=video_resources)
    }

    # Calculate progress percentage
    completed_items = sum(1 for status in user_exercise_progress.values() if status == 'completed') + \
                      sum(1 for status in user_resource_progress.values() if status == 'completed') + \
                      sum(1 for status in user_video_progress.values() if status == 'completed')



    total_items = len(exercises) + len(additional_resources) + len(video_resources)
    progress_value = (completed_items / total_items) * 100 if total_items > 0 else 0

    # Update or create user-specific module progress
    user_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
    user_progress.completion_percentage = progress_value
    user_progress.save()

    context = {
        'module': module,
        'exercises': exercises,
        'additional_resources': additional_resources,
        'video_resources': video_resources,  # Pass videos to template
        'progress_value': progress_value,  
        'user_exercise_progress': user_exercise_progress,  # ✅ Pass user-specific exercise progress
        'user_resource_progress': user_resource_progress,  # ✅ Pass user-specific resource progress
        'user_video_progress': user_video_progress,  # ✅ Pass user-specific video progress
    
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
@login_required
def rate_module(request, module_id):
    """Handles AJAX-based user rating for a module."""
    
    module = get_object_or_404(Module, id=module_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rating_value = int(data.get("rating", 0))

            # reject invalid ratigs
            if not (1 <= rating_value <= 5):
                return JsonResponse({"success": False, "message": "Invalid rating. Must be between 1 and 5."})

            end_user, created = EndUser.objects.get_or_create(user=request.user)

            # update or create the rating
            rating_obj, created = ModuleRating.objects.update_or_create(
                user=end_user,  
                module=module,
                defaults={'rating': rating_value}
            )

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON data"})

    average_rating = module.ratings.aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating else 0

    return JsonResponse({"success": True, "average_rating": average_rating})


@login_required
@csrf_exempt
def mark_done(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get("id")
        item_type = data.get("type")
        action = data.get("action")  # 'done' or 'undo'

        user = request.user
        end_user, created = EndUser.objects.get_or_create(user=user)

        module = None

        if item_type == "resource":
            try:
                resource = AdditionalResource.objects.get(id=item_id)
                user_progress, created = UserResourceProgress.objects.get_or_create(user=end_user, resource=resource)
                user_progress.status = 'completed' if action == "done" else 'not_started'
                user_progress.save()
                module = resource.modules.first()  
            except AdditionalResource.DoesNotExist:
                return JsonResponse({"success": False, "message": "Resource not found."})

        elif item_type == "exercise":
            try:
                exercise = Exercise.objects.get(id=item_id)
                user_progress, created = UserExerciseProgress.objects.get_or_create(user=end_user, exercise=exercise)
                user_progress.status = 'completed' if action == "done" else 'not_started'
                user_progress.save()
                module = exercise.sections.first().modules.first() 
            except Exercise.DoesNotExist:
                return JsonResponse({"success": False, "message": "Exercise not found."})

        elif item_type == "video":
            try:
                video = VideoResource.objects.get(id=item_id)
                user_progress, created = UserVideoProgress.objects.get_or_create(user=end_user, video=video)
                user_progress.status = 'completed' if action == "done" else 'not_started'
                user_progress.save()
                module = video.modules.first() 
            except VideoResource.DoesNotExist:
                return JsonResponse({"success": False, "message": "Video not found."})

        if module:
            user_module_progress, created = UserModuleProgress.objects.get_or_create(user=end_user, module=module)
            user_module_progress.completion_percentage = calculate_progress(end_user, module)
            user_module_progress.save()

            return JsonResponse({
                "success": True,
                "updated_progress": user_module_progress.completion_percentage
            })

        return JsonResponse({"success": False, "message": "Module not found."})

    return JsonResponse({"success": False, "message": "Invalid request."})

@login_required
def unenroll_module(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            module_title = data.get("title")

            # Find the module
            module = Module.objects.filter(title=module_title).first()
            if not module:
                return JsonResponse({"success": False, "error": "Module not found"}, status=404)

            user = request.user
            try:
                end_user = EndUser.objects.get(user=user)
            except EndUser.DoesNotExist:
                return JsonResponse({"success": False, "error": "User not found"}, status=400)

            # Check if the user is enrolled
            enrollment = UserModuleEnrollment.objects.filter(user=end_user, module=module)
            if not enrollment.exists():
                return JsonResponse({"success": False, "error": "Not enrolled"}, status=400)

            # Delete the enrollment
            enrollment.delete()

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def enroll_module(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            module_title = data.get("title")
            if not module_title:
                return JsonResponse({"success": False, "error": "Missing module title"}, status=400)

            # Check if the module exists
            module = Module.objects.filter(title=module_title).first()
            if not module:
                return JsonResponse({"success": False, "error": "Module not found"}, status=404)

            user = request.user
            end_user, created = EndUser.objects.get_or_create(user=user)

            # Check if the user is already enrolled
            if UserModuleEnrollment.objects.filter(user=end_user, module=module).exists():
                return JsonResponse({"success": False, "error": "Already enrolled"}, status=400)

            # Enroll the user
            UserModuleEnrollment.objects.create(user=end_user, module=module)

            return JsonResponse({"success": True})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def all_modules(request):
    allModules = Module.objects.all()  # Fetch all modules
    user = request.user

    # Get the current user's enrolled modules
    try:
        end_user = EndUser.objects.get(user=user)
        enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module__title', flat=True)
    except EndUser.DoesNotExist:
        enrolled_modules = []

    return render(request, 'users/all_modules.html', {
        'all_modules': allModules,
        'enrolled_modules': list(enrolled_modules)  # Convert QuerySet to list
    })

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

@login_required
def journal_view(request, date=None):
    """Loads the journal page and fetches saved data for a specific date."""
    user = request.user

    # Validate & Parse Date
    if date is None:
        selected_date = now().date()
    else:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            selected_date = now().date()  # Default to today if invalid

    # Fetch Journal Entry for the Selected Date
    journal_entry = JournalEntry.objects.filter(user=user, date=selected_date).first()

    # Handle AJAX Requests (Return JSON)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        if journal_entry:
            return JsonResponse({
                "success": True,
                "data": {
                    "sleep_hours": journal_entry.sleep_hours,
                    "caffeine": journal_entry.caffeine,
                    "hydration": journal_entry.hydration,
                    "stress": journal_entry.stress,
                    "goal_progress": journal_entry.goal_progress,
                    "notes": journal_entry.notes,
                    "connected_with_family": journal_entry.connected_with_family,
                    "expressed_gratitude": journal_entry.expressed_gratitude,
                    "outdoors": journal_entry.outdoors,
                    "sunset": journal_entry.sunset,
                }
            })
        return JsonResponse({"success": False, "error": "No entry found."}, status=404)

    # Compute Previous & Next Day
    previous_day = (selected_date - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")

    # Render HTML for Standard Page Load
    context = {
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "journal_entry": journal_entry,
        "previous_day": previous_day,
        "next_day": next_day,
    }

    return render(request, "users/journal.html", context)

@login_required
def save_journal_entry(request):
    """Handles saving/updating journal entries using JSON."""

    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
        print("📥 Received Data:", data)  # Debugging

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)

    date_str = data.get("date")
    if not date_str:
        return JsonResponse({"success": False, "error": "Date is required."}, status=400)

    try:
       entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        
    except ValueError:
        print(f"❌ Invalid Date Received: {date_str}")  # Debugging
        return JsonResponse({"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    # Save the journal entry
    return JsonResponse({"success": True, "message": "Journal entry saved."}, status=201)

