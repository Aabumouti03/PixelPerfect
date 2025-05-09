import json
from datetime import datetime, timedelta
from venv import logger
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg, Q
from django.forms import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from client.models import (
    AdditionalResource,
    Category,
    Exercise,
    ExerciseQuestion,
    Module,
    ModuleRating,
    Program,
    VideoResource,
    Questionnaire,
    Question,


)
from users.helpers_modules import calculate_progress, calculate_program_progress
from users.models import (
    EndUser,
    JournalEntry,
    Questionnaire_UserResponse,
    QuestionResponse,
    StickyNote,
    User,
    UserExerciseProgress,
    UserModuleEnrollment,
    UserModuleProgress,
    UserProgramEnrollment,
    UserResourceProgress,
    UserVideoProgress,
    UserResponse,
    Quote,
)

from .forms import (
    EndUserProfileForm,
    LogInForm,
    UserProfileForm,
    UserSignUpForm,
)
from .helpers_questionnaire import (
    assess_user_responses_modules,
    assess_user_responses_programs,
)

from .utils import send_verification_email_after_sign_up


#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ QUESTIONNAIRE VIEWS --------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


@login_required
def questionnaire(request):
    """Render the questionnaire page for active questionnaires."""
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


@csrf_protect
@login_required
def submit_responses(request):
    """Process and save user questionnaire responses."""
    if request.method == "POST":
        try:
            
            data = json.loads(request.body)
            logger.info("Received data: %s", data)

            try:
                user = EndUser.objects.get(user=request.user)
            except EndUser.DoesNotExist:
                return JsonResponse({"success": False, "message": "User not found. Please sign in."})

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

                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    logger.error("Question with ID %s does not exist.", question_id)
                    continue

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




#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ STICKYNOTE VIEWS -----------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


@login_required
def save_notes(request):
    """Process and save user notes."""
    if request.method == 'POST':
        data = json.loads(request.body)
        content = data.get('content')

        end_user = EndUser.objects.get(user=request.user)

        sticky_note, created = StickyNote.objects.get_or_create(user=end_user)
        sticky_note.content = content
        sticky_note.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def get_notes(request):
    """Fetch and display user notes."""
    try:
        # Get the EndUser instance for the logged-in user
        end_user = EndUser.objects.get(user=request.user)
        sticky_note = StickyNote.objects.get(user=end_user)
        return JsonResponse({'success': True, 'content': sticky_note.content})
    except StickyNote.DoesNotExist:
        return JsonResponse({'success': True, 'content': ''})  # Return empty content if no note exists
    

    

    
#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ DASHBOARD VIEWS ------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

@login_required
def dashboard(request):
    """Render user dashboard page."""
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

   
    user_program_enrollment = UserProgramEnrollment.objects.filter(user=end_user).first()
    program = user_program_enrollment.program if user_program_enrollment else None

    
    program_modules = program.program_modules.all().order_by("order") if program else []

    
    user_progress = {
        progress.module.id: progress.completion_percentage
        for progress in UserModuleProgress.objects.filter(user=end_user)
    }

    previous_module_completed = True
    unlocked_modules = set()

   
    for program_module in program_modules:
        module = program_module.module
        module.progress_value = user_progress.get(module.id, 0)

        if previous_module_completed:
            module.is_unlocked = True
            unlocked_modules.add(module.id)
        else:
            module.is_unlocked = False

        previous_module_completed = module.progress_value == 100

    
    program_progress_value = calculate_program_progress(end_user, program) if program else 0 

    
    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module', flat=True)
    outside_modules = Module.objects.filter(id__in=enrolled_modules).exclude(id__in=[pm.module.id for pm in program_modules])

    
    for module in outside_modules:
        module.progress_value = user_progress.get(module.id, 0)  

    
    recent_enrollments = UserModuleEnrollment.objects.filter(user=end_user).order_by('-last_accessed')[:3]

    recent_modules = [
        enrollment.module for enrollment in recent_enrollments
        if enrollment.module.id and (
            enrollment.module.id in unlocked_modules or
            enrollment.module in outside_modules
        )
    ]

    
    quote_of_the_day = Quote.get_quote_of_the_day()
    
    context = {
        'user': request.user,
        'program': program,
        'program_modules': program_modules,
        'outside_modules': outside_modules,  
        'recent_modules': recent_modules,
        'quote_of_the_day': quote_of_the_day,
        'program_progress_value': program_progress_value,
    }
    return render(request, 'users/dashboard.html', context)


@login_required
def view_program(request, program_id):
    """Display user program details."""
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        return render(request, 'users/program_not_found.html')

    user_program_enrollment = UserProgramEnrollment.objects.filter(user=end_user, program_id=program_id).first()
    
    if not user_program_enrollment:
        return render(request, 'users/program_not_found.html')

    program = user_program_enrollment.program

   
    program_categories = program.categories.all()  

    user_progress = {
        progress.module.id: progress.completion_percentage
        for progress in UserModuleProgress.objects.filter(user=end_user)
    }

    program_modules_data = []
    previous_completed = True

    for index, program_module in enumerate(program.program_modules.all().order_by('order')):
        module = program_module.module
        progress_value = user_progress.get(module.id, 0)  
        is_locked = not previous_completed  

        program_modules_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "progress_value": progress_value,
            "module_order": index + 1,
            "locked": is_locked,
        })

        
        previous_completed = (progress_value == 100)

    context = {
        'user': user,
        'program': program,
        'program_modules': program_modules_data,
        'program_categories': program_categories,  
    }
    
    return render(request, 'users/view_program.html', context)


#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ GENERAL SITE VIEWS ---------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


def welcome_page(request):
    """A function for displaying a page that welcomes users"""
    return render(request, 'users/welcome_page.html')


def about(request):
    """Allows users to get information about the website team"""
    return render(request, 'users/about.html')

def contact_us(request):
    """Allows visitors or users to contact the website team."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = (
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}"
        )

        send_mail(
            subject="New Contact Us Submission",
            message=full_message,
            from_email=settings.EMAIL_HOST_USER,  
            recipient_list=[settings.EMAIL_HOST_USER],  
            fail_silently=False,
        )

        return redirect('contact_success')

    return render(request, 'users/contact_us.html')

def contact_success(request):
    return render(request, 'users/contact_success.html')


@login_required
def get_started(request):
    """Provide the users with option to enroll in modules or programs or start questionnaire."""
    categories = Category.objects.all()

    filter_pressed = "filter" in request.GET
    search_pressed = "search_btn" in request.GET

    search_query = request.GET.get("search", "").strip() if search_pressed else ""
    sort = request.GET.get("sort", None)
    filter_type = request.GET.get("filter_type", "all")
    selected_category_ids = request.GET.getlist("category")
    selected_category_ids = [int(cat_id) for cat_id in selected_category_ids if cat_id.isdigit()]

    # If it's a search (not a filter), reset filters visually and functionally
    if search_pressed and not filter_pressed:
        filter_type = "all"
        selected_category_ids = list(Category.objects.values_list("id", flat=True))

    # If still no categories selected (e.g., initial load), include all
    if not selected_category_ids:
        selected_category_ids = list(Category.objects.values_list("id", flat=True))

    all_categories_selected = set(selected_category_ids) == set(Category.objects.values_list("id", flat=True))

    # Start with all data
    programs = Program.objects.all()
    modules = Module.objects.all()

    if filter_pressed:
        if all_categories_selected or not selected_category_ids:
            programs = programs.filter(
                Q(categories__id__in=selected_category_ids) | Q(categories__isnull=True)
            ).distinct()
            modules = modules.filter(
                Q(categories__id__in=selected_category_ids) | Q(categories__isnull=True)
            ).distinct()
        else:
            programs = programs.filter(categories__id__in=selected_category_ids).distinct()
            modules = modules.filter(categories__id__in=selected_category_ids).distinct()

        if filter_type == "programs":
            modules = Module.objects.none()
        elif filter_type == "modules":
            programs = Program.objects.none()

    if search_pressed and search_query:
        programs = programs.filter(title__icontains=search_query)
        modules = modules.filter(title__icontains=search_query)

    if sort == "asc":
        programs = programs.order_by("title")
        modules = modules.order_by("title")
    elif sort == "desc":
        programs = programs.order_by("-title")
        modules = modules.order_by("-title")

    enrolled_programs = Program.objects.filter(enrolled_users__user=request.user.User_profile)
    enrolled_modules = Module.objects.filter(enrolled_users__user=request.user.User_profile)

    return render(request, "users/get_started.html", {
        "categories": categories,
        "programs": programs,
        "modules": modules,
        "selected_category_ids": selected_category_ids,
        "search_query": search_query,
        "sort": sort,
        "filter_type": filter_type,
        "enrolled_programs": enrolled_programs,
        "enrolled_modules": enrolled_modules,
    })



#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ LOGIN/SIGNUP/VERIFICATION VIEWS --------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


def log_in(request):
    """Allows the users to log in and view their dashboard."""
    error_message = None
    if request.method == "POST":
        form = LogInForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').strip().lower()
            password = form.cleaned_data.get('password').strip()

            user = authenticate(request, username=username, password=password)


            if user is not None:
                if not user.email_verified:
                    error_message = "You must verify your email before logging in."
                else:
                    login(request, user)

                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)

                    # Admin/Client are the only superusers
                    if user.is_superuser:
                        return redirect('client_dashboard')

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

            return render(request, "users/sign_up_email_verification.html")
    else:
        profile_form = EndUserProfileForm()

    return render(request, "users/sign_up_step_2.html", {"profile_form": profile_form})


def sign_up_email_verification(request):
    """Showcases an html page that notifies the user of the next step after signing up."""
    return render(request, "users/sign_up_email_verification.html")


def verify_email_after_sign_up(request, uidb64, token):
    """Verify the user's email after signing up."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return render(request, 'users/invalid_verification.html')

    if default_token_generator.check_token(user, token):
        user.email_verified = True  
        user.save()
        return redirect('verification_done')

    return render(request, 'users/invalid_verification.html')


def verification_done(request):
    """Shows a summary of the user's next steps and takes them to the log in page and then the get started page automatically."""
    return render(request, "users/verification_done.html")


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


def verify_email(request, uidb64, token):
    """Verifies user's email when they change it in the profile section."""
    User = get_user_model()
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return HttpResponse("Invalid verification link.")
    
    if default_token_generator.check_token(user, token):
        if user.new_email:
            user.email = user.new_email 
            user.new_email = None  
            user.email_verified = True  
            user.save()
            
            request.session['profile_update_popup'] = 'profile_updated'
            return redirect('log_in')

    return HttpResponse("Invalid or expired token.")


#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ PROFILE VIEWS --------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


@login_required 
def profile(request):
    """View to display the user profile"""
    user = request.user

    if 'profile_update_popup' in request.session:
        profile_update_popup = request.session['profile_update_popup']

        del request.session['profile_update_popup']
    else:
        profile_update_popup = None

    if hasattr(user, 'User_profile'):
        return render(request, 'users/Profile/profile.html', {'user': user, 'profile_update_popup': profile_update_popup})
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
            user.User_profile.save()  
            user.refresh_from_db()  

            # Handle email change verification
            new_email = form.cleaned_data.get("new_email")
            if new_email:
                new_email = new_email.strip().lower() 
                
                if new_email != user.email.lower():  
                    # Save the new email for verification
                    user.new_email = new_email
                    user.save()

                    # Generate email verification token
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)

                    verification_link = request.build_absolute_uri(f"/verify-email/{uid}/{token}/")

                    send_mail(
                        "Confirm Your Email Change",
                        f"Click the link to confirm your email change: {verification_link}",
                        "noreply@example.com",
                        [new_email],
                        fail_silently=False,
                    )

                    request.session['profile_update_popup'] = 'verification_sent'
                    request.session.save()  
                else:
                    user.new_email = None
                    user.save()

            new_password = form.cleaned_data.get("new_password")
            if new_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)


            return redirect('profile')

        else:
            messages.error(request, "There were errors in the form.")

    else:
        form = UserProfileForm(instance=user.User_profile, user=user)

    return render(request, 'users/Profile/update_profile.html', {'form': form, 'user': user})


@login_required
def delete_account(request):
    """Handle both confirmation page and actual account deletion."""
    user = request.user  # Get the logged-in user

    if request.method == "POST":
        try:
            user.delete()
            logout(request)
            messages.success(request, "Your account has been successfully deleted.")
            return redirect('welcome_page')

        except Exception as e:
            messages.error(request, f"An error occurred while deleting your account: {e}")
            return redirect('profile')  

    context = {'confirmation_text': "Are you sure you want to delete your account? This action cannot be undone."}
    return render(request, 'users/Profile/delete_account.html', context)


#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ PROGRAMS VIEWS -------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

@login_required
def recommended_programs(request):
    """Displays programs for users to enroll in and handles AJAX enrollment updates."""
    user = request.user
    enrolled_programs = Program.objects.filter(enrolled_users__user=user.User_profile)

    end_user = EndUser.objects.get(user=user)

    categorized_programs = assess_user_responses_programs(end_user)

    # all_programs = [program for program_list in categorized_programs.values() for program in program_list]
    all_programs = Program.objects.all()


    if request.method == "POST":
        try:
            data = json.loads(request.body)
            program_id = data.get("program_id")
            action = data.get("action")

            program = Program.objects.get(id=program_id)
            user_profile = user.User_profile

            if action == "enroll":
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


#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ MODULES VIEWS --------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

@login_required
def recommended_modules(request):
    """Displays modules for users to enroll in and handles AJAX enrollment updates."""
    user = request.user
    enrolled_modules = Module.objects.filter(enrolled_users__user=user.User_profile)

    end_user = EndUser.objects.get(user=user)

    categorized_modules = assess_user_responses_modules(end_user)

    all_modules = [module for module_list in categorized_modules.values() for module in module_list]


    if request.method == "POST":
        try:
            data = json.loads(request.body) 
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
    """Display user enrolled modules."""
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
            "progress_value": progress_percentage,  
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
        'video_resources': video_resources,  
        'progress_value': progress_value,  
        'user_exercise_progress': user_exercise_progress,  
        'user_resource_progress': user_resource_progress,  
        'user_video_progress': user_video_progress, 
    
    }

    return render(request, 'users/moduleOverview.html', context)


@login_required
def exercise_detail(request, exercise_id):
    """Display exercise detials."""
    exercise = get_object_or_404(Exercise, id=exercise_id)
    user, _ = EndUser.objects.get_or_create(user=request.user)

    diagram = None
    for section in exercise.sections.all():
        if section.diagram:
            diagram = section.diagram
            break

    if request.method == 'POST':
        for question in exercise.questions.all():
            answer_text = request.POST.get(f'answer_{question.id}', '').strip()

            if answer_text:
                UserResponse.objects.create(
                    user=user,
                    question=question,
                    response_text=answer_text,
                    submitted_at=now()
                )

        messages.success(request, "Your answers have been saved!")
        return redirect('exercise_detail', exercise_id=exercise.id)

    return render(request, 'users/exercise_detail.html', {
        'exercise': exercise,
        'diagram': diagram,
    })

@csrf_exempt  
@login_required
def rate_module(request, module_id):
    """Allows users to rate modules."""
    
    module = get_object_or_404(Module, id=module_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rating_value = int(data.get("rating", 0))

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
    """Allows users to mark tasks as done"""
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
                module = Module.objects.filter(additional_resources=resource).first()  
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
                module = Module.objects.filter(video_resources=video).first()
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
    """Allows users to remove modules from their enrolled modules."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            module_title = data.get("title")
            
            if not module_title:
                return JsonResponse({"success": False, "error": "Missing module title"}, status=400)

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
    """Allows users to add modules to their enrolled modules."""
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
    """Display all available modules."""
    allModules = Module.objects.all()  
    user = request.user
    end_user = None
    try:
        end_user = EndUser.objects.get(user=user)
        enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user).values_list('module__title', flat=True)
    except EndUser.DoesNotExist:
        enrolled_modules = []

    progress_dict = {}
    if end_user:
        user_progress_qs = UserModuleProgress.objects.filter(
            user=end_user, 
            module__in=allModules
        )

        progress_dict = {
            up.module_id: up.completion_percentage 
            for up in user_progress_qs
        }
    
    enrolled_modules = []
    if end_user:
        enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user)\
            .values_list('module__title', flat=True)

    for module in allModules:
        module.progress_value = progress_dict.get(module.id, 0)
    
    return render(request, 'users/all_modules.html', {
        'all_modules': allModules,
        'enrolled_modules': list(enrolled_modules)  # Convert QuerySet to list
    })

@login_required
def welcome_view(request):
    return render(request, 'users/welcome.html')

#-----------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------ JOURNAL VIEWS -------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------

@login_required
def journal_view(request, date=None):
    user = request.user
    if date is None:
        selected_date = now().date()
    else:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            selected_date = now().date()

    journal_entry = JournalEntry.objects.filter(user=user, date=selected_date).first()

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
                    "sunset": journal_entry.sunset
                }
            })
        return JsonResponse({"success": False, "error": "No entry found."}, status=404)

    previous_day = (selected_date - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")

    context = {
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "journal_entry": journal_entry,
        "previous_day": previous_day,
        "next_day": next_day,
    }
    return render(request, "users/journal.html", context)


@login_required
def save_journal_entry(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)

    date_str = data.get("date")
    if not date_str:
        return JsonResponse({"success": False, "error": "Date is required."}, status=400)

    try:
        entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    journal_entry, created = JournalEntry.objects.get_or_create(user=request.user, date=entry_date)

    try:
        journal_entry.sleep_hours = int(data.get("sleep_hours")) if data.get("sleep_hours") is not None else None
    except ValueError:
        journal_entry.sleep_hours = None  # Set to None if the value is invalid

    journal_entry.sleep_hours = data.get("sleep_hours")
    journal_entry.caffeine = data.get("caffeine")
    journal_entry.hydration = data.get("hydration")
    journal_entry.stress = data.get("stress")
    journal_entry.goal_progress = data.get("goal_progress")
    journal_entry.notes = data.get("notes")
    journal_entry.connected_with_family = data.get("connected_with_family")
    journal_entry.expressed_gratitude = data.get("expressed_gratitude")
    journal_entry.outdoors = data.get("outdoors")
    journal_entry.sunset = data.get("sunset")
    journal_entry.save()

    return JsonResponse({"success": True, "message": "Journal entry saved successfully."}, status=201)

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

