from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question, Module,  Program, ProgramModule
from users.models import Questionnaire_UserResponse, QuestionResponse, User
from django.core.paginator import Paginator
from .forms import ProgramForm 



def manage_questionnaires(request):
    search_query = request.GET.get('search', '')  
    is_active_filter = request.GET.get('is_active')
    sort_order = request.GET.get('sort', 'desc')

    # Fetch all questionnaires
    questionnaires = Questionnaire.objects.all()

    # Apply search filter
    if search_query:
        questionnaires = questionnaires.filter(title__icontains=search_query)

    # Apply active filter
    if is_active_filter == 'true':
        questionnaires = questionnaires.filter(is_active=True)

    # Apply sorting
    if sort_order == 'asc':
        questionnaires = questionnaires.order_by('created_at')
    else:
        questionnaires = questionnaires.order_by('-created_at')

    # Get response count
    questionnaires_data = [
        {
            "questionnaire": q,
            "response_count": Questionnaire_UserResponse.objects.filter(questionnaire=q).count()
        }
        for q in questionnaires
    ]

    # Paginate (10 per page)
    paginator = Paginator(questionnaires_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'Manage_Questionnaires.html', {
        'questionnaires_data': page_obj,
        'page_obj': page_obj,
        'is_active_filter': is_active_filter,
        'search_query': search_query,  
        'sort_order': sort_order
    })





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
    search_query = request.GET.get('search', '')  # ✅ Get search query
    responders = Questionnaire_UserResponse.objects.filter(questionnaire=questionnaire).select_related('user')
    
    if search_query:
        responders = responders.filter(
            user__user__first_name__icontains=search_query
        ) | responders.filter(
            user__user__last_name__icontains=search_query
        )
    
    # set 10 requests per page
    paginator = Paginator(responders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'view_responders.html', {
        'questionnaire': questionnaire,
        'responders': page_obj.object_list,
        'page_obj':page_obj
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
            sentiment = request.POST.get(f"sentiment_{question.id}")  # ✅ Get updated sentiment

            if question_text:
                question.question_text = question_text

            if question_type:
                question.question_type = question_type

            if sentiment:
                question.sentiment = int(sentiment)  # ✅ Store updated sentiment

            question.save()

        return redirect("view_questionnaire", questionnaire_id=questionnaire.id)

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

def client_dashboard(request):
    return render(request, 'client/client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
    return render(request, 'client/users_management.html', {'users': users})
    return render(request, 'client/users_management.html', {'users': users})

def modules_management(request):
    modules = Module.objects.all().values("title")
    module_colors = ["color1", "color2", "color3", "color4", "color5", "color6"]
    
    modules_list = []
    for index, module in enumerate(modules):
        module_data = {
            "title": module["title"],
            "color_class": module_colors[index % len(module_colors)]
        }
        modules_list.append(module_data)

    return render(request, "client/modules_management.html", {"modules": modules_list})
    return render(request, "client/modules_management.html", {"modules": modules_list})

def users_management(request):
    users = User.objects.all()
    return render(request, 'client/users_management.html', {'users': users})
    

def programs(request):
    programs = Program.objects.all()
    return render(request, 'client/programs.html', {'programs': programs})

def logout_view(request):
    return render(request, 'client/logout.html')

def create_program(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.save()

            module_order = request.POST.get("module_order", "")
            module_ids = module_order.split(",") if module_order else []

            program.program_modules.all().delete()

            # Add modules in the correct order
            for index, module_id in enumerate(module_ids, start=1):
                try:
                    module = Module.objects.get(id=module_id)
                    ProgramModule.objects.create(program=program, module=module, order=index)
                except Module.DoesNotExist:
                    pass

            return redirect("programs")
    else:
        form = ProgramForm()

    return render(request, "client/create_program.html", {"form": form})


def log_out(request):
    """Confirm logout. If confirmed, redirect to log in. Otherwise, stay."""
    if request.method == "POST":
        logout(request)
        return redirect('users:log_in')

    # if user cancels, stay on the same page
    return render(request, 'client/client_dashboard.html', {'previous_page': request.META.get('HTTP_REFERER', '/')})

def program_detail(request, program_id):
    """ View details of a single program """
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'program_detail.html', {'program': program})

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')
