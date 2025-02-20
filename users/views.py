from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth import authenticate, login, logout
from .forms import UserSignUpForm, EndUserProfileForm, LogInForm
from django.contrib.auth import logout
from .models import Questionnaire, Question, QuestionResponse, Questionnaire_UserResponse, Choice
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib import messages
logger = logging.getLogger(__name__)

def welcome_view(request):
    return render(request, 'welcome.html')

def questionnaire(request):
    active_questionnaire = Questionnaire.objects.filter(is_active=True).first()

    if active_questionnaire:
        questions = Question.objects.filter(questionnaire=active_questionnaire)
        questions_data = [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,  # Add question type
                "choices": [{"id": choice.id, "text": choice.text} for choice in q.choices.all()] if q.question_type == "MULTIPLE_CHOICE" else [],
                "min_rating": q.min_rating if q.question_type == "RATING" else None,
                "max_rating": q.max_rating if q.question_type == "RATING" else None,
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

            user_id = request.user.id  # Ensure the user is authenticated and has an ID
            if not user_id:
                return JsonResponse({"success": False, "message": "User ID is missing. Please log in."})

            questionnaire_id = data.get("questionnaireId")
            responses = data.get("responses", [])

            logger.info("User ID: %s, Questionnaire ID: %s", user_id, questionnaire_id)

            # Ensure questionnaire exists
            questionnaire_user_response, created = Questionnaire_UserResponse.objects.get_or_create(
                user_id=user_id,
                questionnaire_id=questionnaire_id
            )

            for response in responses:
                question_id = response.get("questionId")
                value = response.get("value")

                logger.info("Processing response: %s", response)

                question = Question.objects.get(id=question_id)

                # Create QuestionResponse entry
                question_response = QuestionResponse(
                    user_response=questionnaire_user_response,
                    question=question
                )

                if question.question_type == "MULTIPLE_CHOICE":
                    question_response.selected_choice = Choice.objects.get(id=value)
                elif question.question_type == "RATING":
                    question_response.rating_value = value

                question_response.save()

            return JsonResponse({"success": True, "message": "Responses saved successfully!"})

        except Exception as e:
            logger.error("Error saving responses: %s", str(e))
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method"})


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

    return render(request, 'sign_up_step_2.html', {'profile_form': profile_form})

def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

    # if user cancels, stay on the same page
    return render(request, 'dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})
