from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question
from users.models import Questionnaire_UserResponse, QuestionResponse

def manage_questionnaires(request):
    questionnaires = Questionnaire.objects.all().order_by('-created_at')  
    return render(request, 'Manage_Questionnaires.html', {'questionnaires': questionnaires})


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
            if question_text:
                question.question_text = question_text

            # Handle Rating Question Updates
            if question.question_type == "RATING":
                min_rating = request.POST.get(f"min_rating_{question.id}")
                max_rating = request.POST.get(f"max_rating_{question.id}")
                if min_rating and max_rating:
                    question.min_rating = int(min_rating)
                    question.max_rating = int(max_rating)

            question.save()

        return redirect("manage_questionnaires")

    return render(request, "edit_questionnaire.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })


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
