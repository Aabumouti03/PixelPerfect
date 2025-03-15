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
from users.models import UserProgramEnrollment, EndUser
import random
import datetime

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

QUOTES = [
    "Success is not the key to happiness. Happiness is the key to success. — Albert Schweitzer",
    "Your limitation—it’s only your imagination.",
    "Do what you can, with what you have, where you are. — Theodore Roosevelt",
    "Dream big and dare to fail. — Norman Vaughan",
    "Opportunities don't happen. You create them. — Chris Grosser",
    "Don't let yesterday take up too much of today. — Will Rogers",
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Act as if what you do makes a difference. It does. — William James",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "Every day may not be good, but there's something good in every day.",
    "Keep your face always toward the sunshine—and shadows will fall behind you. — Walt Whitman",
    "You are never too old to set another goal or to dream a new dream. — C.S. Lewis",
    "Difficult roads often lead to beautiful destinations.",
    "You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
    "Happiness is not something ready-made. It comes from your own actions. — Dalai Lama",
    "Work hard in silence, let your success be your noise. — Frank Ocean",
    "Failure is simply the opportunity to begin again, this time more intelligently. — Henry Ford",
    "Live as if you were to die tomorrow. Learn as if you were to live forever. — Mahatma Gandhi",
    "Start where you are. Use what you have. Do what you can. — Arthur Ashe",
    "If you want to lift yourself up, lift up someone else. — Booker T. Washington",
    "No one is perfect—that’s why pencils have erasers. — Wolfgang Riebe",
    "Success is getting what you want. Happiness is wanting what you get. — Dale Carnegie",
    "Happiness depends upon ourselves. — Aristotle",
    "You are capable of amazing things.",
    "Do what makes your soul shine.",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. — Ralph Waldo Emerson",
    "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
    "Small steps in the right direction can turn out to be the biggest step of your life.",
    "Happiness is a direction, not a place. — Sydney J. Harris",
    "If opportunity doesn’t knock, build a door. — Milton Berle",
    "The best way to predict the future is to create it. — Peter Drucker",
    "Be kind whenever possible. It is always possible. — Dalai Lama",
    "You were born to be real, not to be perfect.",
    "Be yourself; everyone else is already taken. — Oscar Wilde",
    "Stay close to anything that makes you glad you are alive. — Hafiz",
    "Enjoy the little things, for one day you may look back and realize they were the big things. — Robert Brault",
    "Your vibe attracts your tribe.",
    "Be strong. You never know who you are inspiring.",
    "Turn your wounds into wisdom. — Oprah Winfrey",
    "Be a voice, not an echo.",
    "With the new day comes new strength and new thoughts. — Eleanor Roosevelt",
    "You are enough just as you are.",
    "A champion is defined not by their wins but by how they can recover when they fall. — Serena Williams",
    "Your life only gets better when you get better.",
    "Happiness is not by chance, but by choice. — Jim Rohn",
    "It always seems impossible until it's done. — Nelson Mandela",
    "Do more of what makes you happy.",
    "Life isn’t about waiting for the storm to pass, it’s about learning to dance in the rain. — Vivian Greene",
    "Success is falling nine times and getting up ten. — Jon Bon Jovi",
    "You didn’t come this far to only come this far.",
    "Some people want it to happen, some wish it would happen, others make it happen. — Michael Jordan",
    "Let your dreams be bigger than your fears.",
    "Doubt kills more dreams than failure ever will. — Suzy Kassem",
    "Every day is a second chance.",
    "The only thing standing between you and your goal is the story you keep telling yourself as to why you can't achieve it. — Jordan Belfort",
    "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne",
    "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
    "Never bend your head. Always hold it high. Look the world straight in the eye. — Helen Keller",
    "Be the reason someone smiles today.",
    "Success isn’t about how much money you make. It’s about the difference you make in people’s lives. — Michelle Obama",
    "You can’t go back and change the beginning, but you can start where you are and change the ending. — C.S. Lewis",
    "Rise above the storm and you will find the sunshine. — Mario Fernandez",
    "Take the risk or lose the chance.",
    "Happiness is letting go of what you think your life is supposed to look like.",
    "A goal without a plan is just a wish. — Antoine de Saint-Exupéry",
    "Fall seven times, stand up eight. — Japanese Proverb",
    "Keep going. Everything you need will come to you at the perfect time.",
    "You are stronger than you think.",
    "Don't compare your life to others. There's no comparison between the sun and the moon, they shine when it's their time.",
    "The only thing you can control is your own effort.",
    "Dare to live the life you have dreamed for yourself. — Ralph Waldo Emerson",
    "Wake up with determination, go to bed with satisfaction.",
    "Make today so awesome that yesterday gets jealous.",
    "Whatever you decide to do, make sure it makes you happy.",
    "Trust the timing of your life.",
    "Everything you can imagine is real. — Pablo Picasso",
    "Your time is limited, so don’t waste it living someone else’s life. — Steve Jobs",
    "Your life does not get better by chance, it gets better by change. — Jim Rohn",
    "What consumes your mind, controls your life.",
    "Stay positive, work hard, make it happen.",
    "Hardships often prepare ordinary people for an extraordinary destiny. — C.S. Lewis",
    "Kindness is a language which the deaf can hear and the blind can see. — Mark Twain",
    "Difficulties in life are intended to make us better, not bitter. — Dan Reeves",
    "The more you give away, the more happy you become. — Dalai Lama",
    "Believe in yourself and all that you are. — Christian D. Larson",
    "Light tomorrow with today. — Elizabeth Barrett Browning",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "Sometimes when you're in a dark place you think you've been buried, but you've actually been planted. — Christine Caine",
    "Optimism is the faith that leads to achievement. — Helen Keller",
    "Happiness often sneaks in through a door you didn’t know you left open. — John Barrymore",
    "It is never too late to be what you might have been. — George Eliot",
    "Difficulties increase the nearer we get to the goal. — Johann Wolfgang von Goethe",
    "In the middle of every difficulty lies opportunity. — Albert Einstein",
    "Happiness is found in doing, not merely possessing. — Napoleon Hill",
    "You miss 100% of the shots you don’t take. — Wayne Gretzky"
]


def get_quote_of_the_day():
    """Selects a quote based on the current date."""
    today = datetime.date.today()
    index = today.toordinal() % len(QUOTES)  # Cycles through quotes based on the day
    return QUOTES[index]

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

    quote_of_the_day = get_quote_of_the_day()
    
    context = {
        'user': user,
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
