from django.shortcuts import redirect, render,  get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import logout
from .models import Questionnaire, Question, Choice
from users.models import Questionnaire_UserResponse, QuestionResponse
from django.contrib import messages


def manage_questionnaires(request):
    questionnaires = Questionnaire.objects.all().order_by('-created_at')  
    return render(request, 'Manage_Questionnaires.html', {'questionnaires': questionnaires})


def activate_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)

    Questionnaire.objects.all().update(is_active=False)

    
    questionnaire.is_active = True
    questionnaire.save()
    
    messages.success(request, f'Activated: {questionnaire.title}')
    return redirect('manage_questionnaires')  # Redirect back to admin panel


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
    responses = QuestionResponse.objects.filter(user_response=user_response_id).select_related('question', 'selected_choice')

    return render(request, 'view_user_response.html', {
        'user_response': user_response,
        'responses': responses,
    })

def edit_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = Question.objects.filter(questionnaire=questionnaire)

    if request.method == "POST":
        # Update title and description
        questionnaire.title = request.POST.get("title")
        questionnaire.description = request.POST.get("description")
        questionnaire.save()

        # Update existing questions and choices
        for question in questions:
            question_text = request.POST.get(f"question_text_{question.id}")
            if question_text:
                question.question_text = question_text
                question.save()

            if question.question_type == "MULTIPLE_CHOICE":
                for choice in question.choices.all():
                    choice_text = request.POST.get(f"choice_text_{choice.id}")
                    if choice_text:
                        choice.text = choice_text
                        choice.save()

            elif question.question_type == "RATING":
                min_rating = request.POST.get(f"min_rating_{question.id}")
                max_rating = request.POST.get(f"max_rating_{question.id}")
                if min_rating and max_rating:
                    question.min_rating = int(min_rating)
                    question.max_rating = int(max_rating)
                    question.save()

        return redirect("manage_questionnaires")  # Redirect to the manage page after saving

    return render(request, "edit_questionnaire.html", {
        "questionnaire": questionnaire,
        "questions": questions
    })

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    questionnaire_id = question.questionnaire.id
    question.delete()
    return redirect("edit_questionnaire", questionnaire_id=questionnaire_id)

def delete_choice(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    question_id = choice.question.id
    choice.delete()
    return redirect("edit_questionnaire", questionnaire_id=choice.question.questionnaire.id)

def add_question(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    
    # Create a blank question and redirect to edit page
    new_question = Question.objects.create(
        questionnaire=questionnaire,
        question_text="New Question",
        question_type="MULTIPLE_CHOICE",
        is_required=True
    )
    
    return redirect("edit_questionnaire", questionnaire_id=questionnaire.id)
