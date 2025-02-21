from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question
from users.models import Questionnaire_UserResponse, QuestionResponse

def manage_questionnaires(request):
    questionnaires = Questionnaire.objects.all().order_by('-created_at')  

    # Get response count for each questionnaire
    questionnaires_data = [
        {
            "questionnaire": q,
            "response_count": Questionnaire_UserResponse.objects.filter(questionnaire=q).count()
        }
        for q in questionnaires
    ]

    return render(request, 'Manage_Questionnaires.html', 
                  {'questionnaires_data': questionnaires_data})



def activate_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)

    # Ensure only one questionnaire is active
    Questionnaire.objects.all().update(is_active=False)
    questionnaire.is_active = True
    questionnaire.save()
    
    messages.success(request, f'Activated: {questionnaire.title}')
    return redirect('manage_questionnaires')


def view_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = Question.objects.filter(questionnaire=questionnaire)

    return render(request, 'view_questionnaire.html', {
        'questionnaire': questionnaire,
        'questions': questions
    })


def view_responders(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    responders = Questionnaire_UserResponse.objects.filter(questionnaire=questionnaire).select_related('user')

    return render(request, 'view_responders.html', {
        'questionnaire': questionnaire,
        'responders': responders,
    })


def view_user_response(request, user_response_id):
    user_response = get_object_or_404(Questionnaire_UserResponse, id=user_response_id)
    responses = QuestionResponse.objects.filter(user_response=user_response_id).select_related('question')

    return render(request, 'view_user_response.html', {
        'user_response': user_response,
        'responses': responses,
    })

def create_questionnaire(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        # Create new questionnaire
        questionnaire = Questionnaire.objects.create(title=title, description=description)

        # Retrieve all questions
        question_index = 0
        while f"question_text_{question_index}" in request.POST:
            question_text = request.POST.get(f"question_text_{question_index}")
            question_type = request.POST.get(f"question_type_{question_index}")
            sentiment = int(request.POST.get(f"sentiment_{question_index}", 1))  # Default positive

            # Create the question
            Question.objects.create(
                questionnaire=questionnaire,
                question_text=question_text,
                question_type=question_type,
                sentiment=sentiment
            )

            question_index += 1  # Move to next question

        messages.success(request, "Questionnaire created successfully!")
        return redirect("manage_questionnaires")

    return render(request, "create_questionnaire.html")

def edit_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = Question.objects.filter(questionnaire=questionnaire)

    if request.method == "POST":
        # Update questionnaire title and description
        questionnaire.title = request.POST.get("title")
        questionnaire.description = request.POST.get("description")
        questionnaire.save()

        # Update existing questions
        for question in questions:
            question_text = request.POST.get(f"question_text_{question.id}")
            question_type = request.POST.get(f"question_type_{question.id}")  # ✅ Get question type from form

            if question_text:
                question.question_text = question_text

            if question_type:  # ✅ Update question type
                question.question_type = question_type

            question.save()

        return redirect("view_questionnaire",  questionnaire_id=questionnaire.id)

    return render(request, "edit_questionnaire.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })

def delete_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questionnaire.delete()
    return redirect("manage_questionnaires")

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    questionnaire_id = question.questionnaire.id
    question.delete()
    return redirect("edit_questionnaire", questionnaire_id=questionnaire_id)



def add_question(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    
    # Default to Agreement Scale when creating a new question
    new_question = Question.objects.create(
        questionnaire=questionnaire,
        question_text="New Question",
        question_type="AGREEMENT",
        is_required=True
    )
    
    return redirect("edit_questionnaire", questionnaire_id=questionnaire.id)



