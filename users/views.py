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
from django.conf import settings
import random
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
    return render(request, 'users/welcome_page.html')


def modules(request):
    return render(request, 'users/modules.html')

def profile(request):
    return render(request, 'users/profile.html')

def about(request):
    return render(request, 'users/about.html')

def contact_us(request):
    return render(request, 'users/contact_us.html')

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

    return render(request, 'users/log_in.html', {'form': form})


#A function for displaying a sign up page
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

    return render(request, 'users/sign_up_step_1.html', {'user_form': user_form})

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

    return render(request, 'users/sign_up_step_2.html', {'profile_form': profile_form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
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


def module_overview(request, id):
    module = get_object_or_404(Module, id=id)

    try:
        end_user = EndUser.objects.get(user=request.user)
    except EndUser.DoesNotExist:
        return HttpResponse("EndUser profile does not exist. Please contact support.")

    progress = UserModuleProgress.objects.filter(module=module, user=end_user).first()
    progress_value = progress.completion_percentage if progress else 0

    return render(request, 'moduleOverview2.html', {'module': module, 'progress_value': progress_value})


@login_required
def user_modules(request):
    user = request.user

    try:
        end_user = EndUser.objects.get(user=user)
    except EndUser.DoesNotExist:
        end_user = EndUser.objects.create(user=user)

    enrolled_modules = UserModuleEnrollment.objects.filter(user=end_user)

    background_folder = os.path.join(settings.BASE_DIR, 'static/img/backgrounds')
    
    background_images = os.listdir(background_folder)
    
    module_data = []

    for enrollment in enrolled_modules:
        module = enrollment.module
        progress = UserModuleProgress.objects.filter(user=end_user, module=module).first()

        progress_percentage = progress.completion_percentage if progress else 0

        background_image = random.choice(background_images)

        module_data.append({
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "progress": progress_percentage,
            "background_image": f'img/backgrounds/{background_image}' 
        })

    return render(request, 'userModules.html', {"module_data": module_data})


def all_modules(request):
    modules = Module.objects.all()

    return render(request, 'all_modules.html', {'modules': modules})

def logout_view(request):
    return render(request, 'users/logout.html')

@login_required
def journal(request):
    return render(request, 'users/journal.html')


@login_required
def journal_view(request, date=None):
    """Loads the journal page and fetches saved data for a specific date"""
    user = request.user

    # Use today's date if none is provided
    if date is None:
        selected_date = datetime.now().date()
    else:
        try:
            selected_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            print(f"⚠️ Invalid date format received: {date}, defaulting to today.")
            selected_date = datetime.now().date()

    # Fetch the journal entry for the selected date (if it exists)
    journal_entry = JournalEntry.objects.filter(user=user, date=selected_date).first()

    if journal_entry:
        print(f"✅ Found Journal Entry for {selected_date}: {journal_entry}")
    else:
        print(f"❌ No Journal Entry Found for {selected_date}")

    # Get previous and next days
    previous_day = selected_date - timedelta(days=1)
    next_day = selected_date + timedelta(days=1)

    context = {
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "journal_entry": journal_entry,  # Might be None if no entry exists
        "previous_day": previous_day.strftime("%Y-%m-%d"),
        "next_day": next_day.strftime("%Y-%m-%d"),
    }
    return render(request, "users/journal.html", context)


@csrf_exempt
@login_required
def save_journal_entry(request):
    """Handles saving journal entries using JSON"""
    if request.method == "POST":
        try:
            print("✅ Received POST request to save journal entry")

            # Load JSON data
            try:
                data = json.loads(request.body)
                print("📤 Data received:", data)  # Debugging message
            except json.JSONDecodeError as e:
                print("❌ JSON Decode Error:", str(e))
                return JsonResponse({"success": False, "error": "Invalid JSON format"}, status=400)

            user = request.user
            date_str = data.get("date", datetime.now().date().strftime("%Y-%m-%d"))

            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("⚠️ Invalid date format:", date_str)
                return JsonResponse({"success": False, "error": "Invalid date format."}, status=400)

            # Get or create journal entry
            journal_entry, created = JournalEntry.objects.get_or_create(user=user, date=entry_date)

            # Update entry with new values
            journal_entry.sleep_hours = data.get("sleep_hours")
            journal_entry.coffee = data.get("coffee")
            journal_entry.hydration = data.get("hydration")
            journal_entry.stress = data.get("stress")
            journal_entry.notes = data.get("notes")
            journal_entry.save()

            print("✅ Successfully saved journal entry for", entry_date)

            return JsonResponse({"success": True, "message": "Journal entry saved successfully!"})

        except Exception as e:
            print("❌ Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)



@csrf_exempt
@login_required
def journal_submit(request):
    """Handles saving journal entries using JSON."""
    if request.method == "POST":
        try:
            # Debug: Print incoming data
            print("📥 [SERVER] Received Request:", request.body)

            data = json.loads(request.body.decode("utf-8"))  # Decode JSON request
            user = request.user
            date_str = data.get("date")
            if not date_str:
                return JsonResponse({"success": False, "error": "Date is required."}, status=400)

            # Convert date string into the proper format (YYYY-MM-DD)
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()  # Expecting "2025-03-02"
            except ValueError:
                return JsonResponse({"success": False, "error": "Invalid date format."}, status=400)

            # Get or create journal entry
            journal_entry, created = JournalEntry.objects.get_or_create(user=user, date=entry_date)

            # Update the entry with provided data
            journal_entry.sleep_hours = data.get("sleep_hours") or None
            journal_entry.coffee = data.get("coffee") or None
            journal_entry.hydration = data.get("hydration") or None
            journal_entry.stress = data.get("stress") or None
            journal_entry.notes = data.get("notes") or None
            journal_entry.save()

            print("✅ [SERVER] Journal entry saved successfully!")

            return JsonResponse({"success": True, "message": "Journal entry saved successfully!"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format."}, status=400)

        except Exception as e:
            print("❌ [SERVER ERROR]", str(e))  # Debugging
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)
