
from django.shortcuts import render, redirect, get_object_or_404, redirect, get_object_or_404
from client.models import Program, Module
from django.shortcuts import render, get_object_or_404
from client.models import Module, Category
from collections import Counter
import json
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Questionnaire, Question, Module,  Program, ProgramModule
from users.models import Questionnaire_UserResponse, QuestionResponse, User
from django.core.paginator import Paginator
from .forms import ProgramForm, CategoryForm
from .models import Program, ProgramModule, Category
from client.statistics import * 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
import csv
from django.db import transaction 
from django.db.models import Max
from client import views as clientViews
from users import views as usersViews
from users.views import enroll_module, unenroll_module 
from django.contrib import messages
from .models import Questionnaire, Question, Module,  Program, ProgramModule, Category
from users.models import Questionnaire_UserResponse, QuestionResponse, User
from django.core.paginator import Paginator
from .forms import ProgramForm 
from django.contrib.auth.decorators import login_required

def admin_check(user):
    return user.is_authenticated and user.is_superuser

from .forms import ModuleForm, SectionForm, ExerciseForm,ExerciseQuestionForm
from .models import Module, Section, Exercise, Question, ExerciseQuestion
from django.db import transaction
from django.http import JsonResponse
from collections import defaultdict


def CreateModule(request):
    modules = Module.objects.prefetch_related("sections__exercises__questions").all()
    return render(request, "Module/Edit_Add_Module.html", {"modules": modules})

def edit_module(request, module_id):
    """Handles editing an existing module."""
    module = get_object_or_404(Module, id=module_id)

    # Get sections **NOT** already in this module
    all_sections = Section.objects.exclude(id__in=module.sections.values_list('id', flat=True))

    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated successfully!")
            return redirect('client_modules')  # Redirect to module list
        else:
            messages.error(request, "Error updating module. Please check the form.")
    else:
        form = ModuleForm(instance=module)

    return render(request, 'Module/edit_module.html', {
        'form': form,
        'module': module,
        'all_sections': all_sections  # ✅ Pass sections to template
    })

def edit_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    # ✅ Fetch all exercises **NOT** already in this section
    all_exercises = Exercise.objects.exclude(id__in=section.exercises.values_list('id', flat=True))

    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated successfully!")
            return redirect('edit_module', section.modules.first().id)

    else:
        form = SectionForm(instance=section)

    return render(request, 'Module/edit_section.html', {
        'form': form,
        'section': section,
        'all_exercises': all_exercises,
    })


@csrf_exempt
def update_module(request, module_id):
    """Updates the module title or description based on AJAX request."""
    if request.method == 'POST':
        module = get_object_or_404(Module, id=module_id)
        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            if field == 'title':
                module.title = value
            elif field == 'description':
                module.description = value
            else:
                return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

            module.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@csrf_exempt
def add_section_to_module(request, module_id):
    """Handles adding a section to a module via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            section_id = data.get("section_id")

            module = get_object_or_404(Module, id=module_id)
            section = get_object_or_404(Section, id=section_id)

            module.sections.add(section)

            return JsonResponse({"success": True, "message": "Section added successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@csrf_exempt
def remove_section_from_module(request, module_id):
    """Handles removing sections from a module via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            section_ids = data.get("section_ids", [])

            module = get_object_or_404(Module, id=module_id)
            module.sections.remove(*section_ids)

            return JsonResponse({"success": True, "message": "Sections removed successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id)
    if request.method == "POST":
        form = ExerciseForm(request.POST, instance=exercise)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercise updated successfully!")
            return redirect('edit_section', exercise.sections.first().id)
    else:
        form = ExerciseForm(instance=exercise)
    return render(request, 'Module/edit_exercise.html', {'form': form, 'exercise': exercise})

@csrf_exempt
def update_section(request, section_id):
    """Updates the section title or description via AJAX request."""
    if request.method == 'POST':
        section = get_object_or_404(Section, id=section_id)
        
        try:
            data = json.loads(request.body)
            field = data.get('field')
            value = data.get('value')

            if field == 'title':
                section.title = value
            elif field == 'description':
                section.description = value
            else:
                return JsonResponse({'success': False, 'error': 'Invalid field'}, status=400)

            section.save()
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@csrf_exempt
def add_exercise_to_section(request, section_id):
    """Handles adding an exercise to a section via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            exercise_id = data.get("exercise_id")

            section = get_object_or_404(Section, id=section_id)
            exercise = get_object_or_404(Exercise, id=exercise_id)

            section.exercises.add(exercise)

            return JsonResponse({"success": True, "message": "Exercise added successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@csrf_exempt
def remove_exercise_from_section(request, section_id):
    """Handles removing exercises from a section via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            exercise_ids = data.get("exercise_ids", [])  # ✅ Ensure it's a list

            section = get_object_or_404(Section, id=section_id)

            print(f"🔍 Received request to remove exercises: {exercise_ids}")  # Debugging
            print(f"📌 Current exercises in section: {list(section.exercises.values_list('id', flat=True))}")  # Debugging

            if not exercise_ids:
                return JsonResponse({"success": False, "error": "No exercise IDs received."}, status=400)

            # ✅ Remove exercises
            section.exercises.remove(*exercise_ids)

            print(f"✅ Updated exercises in section: {list(section.exercises.values_list('id', flat=True))}")  # Debugging

            return JsonResponse({"success": True, "message": "Exercises removed successfully!"})
        except Exception as e:
            print(f"❌ Error: {e}")  # Debugging
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def manage_exercises(request):
    """Renders a page displaying all exercises with their questions."""
    exercises = Exercise.objects.prefetch_related('questions').all()

    return render(request, 'Module/manage_exercises.html', {
        'exercises': exercises
    })

@csrf_exempt
def update_exercise(request, exercise_id):
    """Handles updating an exercise title and its questions via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            exercise = get_object_or_404(Exercise, id=exercise_id)

            # Update Exercise Title
            exercise.title = data.get("title", exercise.title)
            exercise.save()

            # Update Questions
            for question_data in data.get("questions", []):
                question = get_object_or_404(ExerciseQuestion, id=question_data["id"])
                question.question_text = question_data["text"]
                question.save()

            return JsonResponse({"success": True, "message": "Exercise updated successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@csrf_exempt
def delete_exercise_questions(request, exercise_id):
    """Handles deleting selected exercise questions via AJAX."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question_ids = data.get("question_ids", [])

            if not question_ids:
                return JsonResponse({"success": False, "error": "No questions selected"}, status=400)

            # ✅ Delete selected questions
            deleted_count, _ = ExerciseQuestion.objects.filter(id__in=question_ids).delete()

            return JsonResponse({"success": True, "message": f"{deleted_count} questions deleted!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

def add_module(request):
    """Handles adding a module with multiple sections."""
    form_data = request.session.get('module_form_data', {})  # Load stored data
    form = ModuleForm(initial=form_data) if form_data else ModuleForm()

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.save()
            form.save_m2m()  # Save many-to-many relationship
            
            request.session.pop('module_form_data', None)  # Clear stored data after save
            return redirect('modules')  

        request.session['module_form_data'] = request.POST  # Save form data if invalid

    sections = Section.objects.all()
    return render(request, 'Module/add_module.html', {'form': form, 'sections': sections})

def add_section(request):
    """Handles the addition of a new section with title, description, and exercises."""
    form = SectionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('add_module')

    exercises = Exercise.objects.all()  # ✅ Fetch all exercises
    return render(request, 'Module/add_section.html', {'form': form, 'exercises': exercises})

def get_sections(request):
    """Returns all sections as JSON (for dynamically updating dropdown)."""
    sections = list(Section.objects.values('id', 'title'))
    return JsonResponse({'sections': sections})
   
def add_exercise(request):
    """Handles adding a new exercise with title, type, and related questions."""
    form = ExerciseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('add_section')

    questions = ExerciseQuestion.objects.all()  # ✅ Fetch all questions
    return render(request, 'Module/add_exercise.html', {'form': form, 'questions': questions})
  

def add_Equestion(request):
    """Handles adding a new question with only the required fields."""
    form = ExerciseQuestionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('add_exercise')  # ✅ Redirect back to add exercise page

    return render(request, 'Module/add_question.html', {'form': form})


@login_required
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

    return render(request, 'client/Manage_Questionnaires.html', {
        'questionnaires_data': page_obj,
        'page_obj': page_obj,
        'is_active_filter': is_active_filter,
        'search_query': search_query,  
        'sort_order': sort_order
    })

@login_required
def activate_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)

    # Ensure only one questionnaire is active
    Questionnaire.objects.all().update(is_active=False)
    questionnaire.is_active = True
    questionnaire.save()
    
    messages.success(request, f'Activated: {questionnaire.title}')
    return redirect('manage_questionnaires')

@login_required
def view_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = Question.objects.filter(questionnaire=questionnaire)

    return render(request, 'client/view_questionnaire.html', {
        'questionnaire': questionnaire,
        'questions': questions
    })

@login_required
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

    return render(request, 'client/view_responders.html', {
        'questionnaire': questionnaire,
        'responders': page_obj.object_list,
        'page_obj':page_obj
    })

@login_required
def view_user_response(request, user_response_id):
    user_response = get_object_or_404(Questionnaire_UserResponse, id=user_response_id)
    responses = QuestionResponse.objects.filter(user_response=user_response_id).select_related('question')

    return render(request, 'client/view_user_response.html', {
        'user_response': user_response,
        'responses': responses,
    })
@login_required
def create_questionnaire(request):
    categories = Category.objects.all()
    sentiment_choices = Question.SENTIMENT_CHOICES  

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")

        questionnaire = Questionnaire.objects.create(title=title, description=description)

        question_index = 0
        while f"question_text_{question_index}" in request.POST:
            question_text = request.POST.get(f"question_text_{question_index}")
            question_type = request.POST.get(f"question_type_{question_index}")
            sentiment = int(request.POST.get(f"sentiment_{question_index}", 1))  
            category_id = request.POST.get(f"category_{question_index}")
            category = Category.objects.get(id=category_id) if category_id else None  

            Question.objects.create(
                questionnaire=questionnaire,
                question_text=question_text,
                question_type=question_type,
                sentiment=sentiment,
                category=category
            )

            question_index += 1  

        messages.success(request, "Questionnaire created successfully!")
        return redirect("manage_questionnaires")

    return render(request, "client/create_questionnaire.html", {
        "categories": categories,
        "sentiment_choices": sentiment_choices,  
    })

@login_required
def edit_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questions = Question.objects.filter(questionnaire=questionnaire)
    categories = Category.objects.all()
    sentiment_choices = Question.SENTIMENT_CHOICES  # ✅ Get choices from model

    if request.method == "POST":
        questionnaire.title = request.POST.get("title")
        questionnaire.description = request.POST.get("description")
        questionnaire.save()

        for question in questions:
            question_text = request.POST.get(f"question_text_{question.id}")
            question_type = request.POST.get(f"question_type_{question.id}")
            sentiment = request.POST.get(f"sentiment_{question.id}")
            category_id = request.POST.get(f"category_{question.id}")

            if question_text:
                question.question_text = question_text

            if question_type:
                question.question_type = question_type

            if sentiment:
                question.sentiment = int(sentiment)  

            if category_id:
                question.category = Category.objects.get(id=category_id)

            question.save()

        return redirect("view_questionnaire", questionnaire_id=questionnaire.id)

    return render(request, "client/edit_questionnaire.html", {
        "questionnaire": questionnaire,
        "questions": questions,
        "categories": categories,
        "sentiment_choices": sentiment_choices,  
    })

@login_required
def delete_questionnaire(request, questionnaire_id):
    questionnaire = get_object_or_404(Questionnaire, id=questionnaire_id)
    questionnaire.delete()
    return redirect("manage_questionnaires")
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    questionnaire_id = question.questionnaire.id
    question.delete()
    return redirect("edit_questionnaire", questionnaire_id=questionnaire_id)

@login_required
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

from .forms import ProgramForm, CategoryForm
from .models import Program, ProgramModule, Module
import json
from client.statistics import * 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
import csv

def admin_check(user):
    return user.is_authenticated and user.is_superuser


# Create your views here.
def client_dashboard(request):

    # GENERAL STATISTICS IN THE DASHBOARD
    enrollment_labels, enrollment_data = get_module_enrollment_stats()  
    last_work_time_labels, last_work_time_data = get_users_last_work_time()
    users_count = EndUser.objects.all()

    return render(request, 'client/client_dashboard.html' , {
        'users_count':len(users_count),
        'enrollment_labels': json.dumps(enrollment_labels),
        'enrollment_data': json.dumps(enrollment_data),
        'last_work_time_labels': json.dumps(last_work_time_labels),
        'last_work_time_data': json.dumps(last_work_time_data),
    })

def users_management(request):
    users = EndUser.objects.all()
    return render(request, 'client/users_management.html', {'users': users})

def user_detail_view(request, user_id):
    user_profile = get_object_or_404(EndUser, user__id=user_id)

    # Get enrolled programs & modules
    enrolled_programs = UserProgramEnrollment.objects.filter(user=user_profile).select_related('program')
    enrolled_modules = UserModuleEnrollment.objects.filter(user=user_profile).select_related('module')

    user_questionnaire_responses = Questionnaire_UserResponse.objects.filter(
        user=user_profile
    ).prefetch_related("questionnaire", "question_responses__question")

    # Group responses by questionnaire
    questionnaires_with_responses = {}
    for user_response in user_questionnaire_responses:
        if user_response.questionnaire not in questionnaires_with_responses:
            questionnaires_with_responses[user_response.questionnaire] = []
        for response in user_response.question_responses.all():
            questionnaires_with_responses[user_response.questionnaire].append(response)

    context = {
        'user': user_profile,
        'enrolled_programs': enrolled_programs,
        'enrolled_modules': enrolled_modules,
        'questionnaires_with_responses': questionnaires_with_responses,  # 👈 Fixed context structure
    }
    return render(request, 'client/user_detail.html', context)

def programs(request):
    programs = Program.objects.prefetch_related('program_modules__module').all()
    return render(request, 'client/programs.html', {'programs': programs})

@login_required
@user_passes_test(admin_check)
def create_program(request):
    categories = Category.objects.all()

    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program_title = form.cleaned_data.get("title")

            if Program.objects.filter(title__iexact=program_title).exists():
                form.add_error("title", "A program with this title already exists.")

            else:
                program = form.save(commit=False)
                program.save()

            
                module_order = request.POST.get("module_order", "").strip()
                if module_order:
                    module_ids = module_order.split(",")
                    ProgramModule.objects.filter(program=program).delete()

                    for index, module_id in enumerate(module_ids, start=1):
                        if module_id.isdigit(): #making sure the javascript works properly
                            module = Module.objects.filter(id=int(module_id)).first()
                            if module:
                                ProgramModule.objects.create(program=program, module=module, order=index)

                return redirect("programs")

    else:
        form = ProgramForm()

    return render(request, "client/create_program.html", {
        "form": form,
        "categories": categories,
    })

@login_required
@user_passes_test(admin_check)
def log_out_client(request):
    if request.method == "POST":
        logout(request)
        return redirect('log_in')

    return redirect('/client_dashboard/')


def program_detail(request, program_id): 
    program = get_object_or_404(Program, id=program_id)
    all_modules = Module.objects.all()
    program_modules = program.program_modules.all()  
    program_module_ids = list(program_modules.values_list('module_id', flat=True)) 

    enrolled_users = program.enrolled_users.all()
    enrolled_user_ids = set(enrollment.user_id for enrollment in enrolled_users)

    if request.method == "POST":
        if "remove_module" in request.POST:
            module_id = request.POST.get("remove_module")
            program_module = ProgramModule.objects.filter(program=program, module_id=module_id).first()
            if program_module:
                program_module.delete()
            return redirect("program_detail", program_id=program.id)

        if "add_modules" in request.POST:
            modules_to_add = request.POST.getlist("modules_to_add")
            max_order = program.program_modules.aggregate(Max('order'))['order__max'] or 0
            for index, m_id in enumerate(modules_to_add, start=1):
                module_obj = get_object_or_404(Module, id=m_id)
                ProgramModule.objects.create(program=program, module=module_obj, order=max_order + index)
            return redirect("program_detail", program_id=program.id)

    context = {
        "program": program,
        "all_modules": all_modules,
        "program_modules": program_modules,  
        "program_module_ids": program_module_ids,
        "enrolled_users": enrolled_users,
    }

    return render(request, "client/program_detail.html", context)

@csrf_exempt
def update_module_order(request, program_id):
    """Handles module reordering in a program while preventing UNIQUE constraint errors."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            program = get_object_or_404(Program, id=program_id)
            order_mapping = {int(item["id"]): index + 1 for index, item in enumerate(data["order"])}

            with transaction.atomic():
                temp_order = 1000  
                for module_id in order_mapping.keys():
                    ProgramModule.objects.filter(id=module_id, program=program).update(order=temp_order)
                    temp_order += 1 

                for module_id, new_order in order_mapping.items():
                    ProgramModule.objects.filter(id=module_id, program=program).update(order=new_order)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

def delete_program(request, program_id):
    """ Delete a program and redirect to the programs list """
    program = get_object_or_404(Program, id=program_id)
    program.delete()
    return redirect('programs')


def category_list(request):
    categories = Category.objects.all()

    context = {
        'categories': categories,
    }
    
    return render(request, 'client/category_list.html', context)

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    programs = category.programs.all()
    modules = category.modules.all()

    context = {
        'category': category,
        'programs': programs,
        'modules': modules,
    }

    return render(request, 'client/category_detail.html', context)

def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()

            modules = form.cleaned_data['modules']
            programs = form.cleaned_data['programs']

            category.modules.set(modules)
            category.programs.set(programs)

            return redirect('category_list')
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }

    return render(request, 'client/create_category.html', context)

def reports(request):
    # THREE CATEGORIES USERS - MODULES - PROGRAMMS 
    enrollment_labels, enrollment_data = get_module_enrollment_stats() # 1 for modules 
    last_work_labels, last_work_data = get_users_last_work_time() #  2 for users
    program_labels, program_data = get_program_enrollment_stats() # 3 for programs

    return render(request, 'client/reports.html', {
            'enrollment_labels': json.dumps(enrollment_labels),
            'enrollment_data': json.dumps(enrollment_data),  
            'last_work_labels': json.dumps(last_work_labels),
            'last_work_data': json.dumps(last_work_data),
            'program_labels': json.dumps(program_labels),
            'program_data': json.dumps(program_data),
        })

def modules_statistics(request):
    """Main view function to fetch and pass module statistics."""
    enrollment_labels, enrollment_data = get_module_enrollment_stats()
    completion_labels, completed_data, in_progress_data = get_module_completion_stats()
    avg_completion_labels, avg_completion_data = get_average_completion_percentage()
    modules_count = get_modules_count()

    return render(request, 'client/modules_statistics.html', {
        'modules_count': modules_count,
        'enrollment_labels': json.dumps(enrollment_labels),
        'enrollment_data': json.dumps(enrollment_data),
        'completion_labels': json.dumps(completion_labels),
        'completed_data': json.dumps(completed_data),
        'in_progress_data': json.dumps(in_progress_data),
        'completion_time_labels': json.dumps(avg_completion_labels),
        'completion_time_data': json.dumps(avg_completion_data),  
    })

def programs_statistics(request):
    """Main view function to fetch and pass program statistics."""
    
    program_labels, program_data = get_program_enrollment_stats()
    completion_labels, completed_data, in_progress_data = get_program_completion_stats()
    avg_completion_labels, avg_completion_data = get_average_program_completion_percentage()
    programs_count = get_programs_count()

    return render(request, 'client/programs_statistics.html', {
        'program_labels': json.dumps(program_labels),
        'program_data': json.dumps(program_data),
        'completion_labels': json.dumps(completion_labels),
        'completed_data': json.dumps(completed_data),
        'in_progress_data': json.dumps(in_progress_data),
        'completion_time_labels': json.dumps(avg_completion_labels),
        'completion_time_data': json.dumps(avg_completion_data),  
        'programs_count': programs_count
    })

'''
The userStatistics method is responsible for generating user statistics for reports. 
It gathers various metrics about users and their enrollments in programs and 
returns them in a JSON format to be displayed in the User Statistics Dashboard.

'''
def userStatistics(request):
    total_users = EndUser.objects.count()
    active_users = EndUser.objects.filter(user__is_active=True).count()
    inactive_users = total_users - active_users
    total_programs_enrolled = UserProgramEnrollment.objects.count()

    # Get gender distribution
    gender_counts = dict(Counter(EndUser.objects.values_list('gender', flat=True)))
    
    # Get ethnicity distribution
    ethnicity_counts = dict(Counter(EndUser.objects.values_list('ethnicity', flat=True)))
    
    # Get sector distribution
    sector_counts = dict(Counter(EndUser.objects.values_list('sector', flat=True)))

    # Pass data as JSON
    stats_data = {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "programs_enrolled": total_programs_enrolled,
        "gender_distribution": gender_counts,
        "ethnicity_distribution": ethnicity_counts,
        "sector_distribution": sector_counts,
    }

    return render(request, "client/userStatistics.html", {"stats": json.dumps(stats_data)})  # ✅ Pass JSON data



def export_modules_statistics_csv(request):
    """Generate a CSV report of module statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="modules_statistics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
    modules_count = get_modules_count()
    writer.writerow(["Total Modules", modules_count])

    enrollment_labels, enrollment_data = get_module_enrollment_stats()
    for label, value in zip(enrollment_labels, enrollment_data):
        writer.writerow([f"Enrollment - {label}", value])

    completion_labels, completed_data, in_progress_data = get_module_completion_stats()
    for label, comp, in_prog in zip(completion_labels, completed_data, in_progress_data):
        writer.writerow([f"Completion - {label} (Completed)", comp])
        writer.writerow([f"Completion - {label} (In Progress)", in_prog])

    avg_completion_labels, avg_completion_data = get_average_completion_percentage()
    for label, value in zip(avg_completion_labels, avg_completion_data):
        writer.writerow([f"Avg Completion - {label}", value])

    return response

def export_programs_statistics_csv(request):
    """Generate a CSV report of program statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="programs_statistics.csv"'
    
    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
    programs_count = get_programs_count()
    writer.writerow(["Total Programs", programs_count])

    enrollment_labels, enrollment_data = get_program_enrollment_stats()
    for label, value in zip(enrollment_labels, enrollment_data):
        writer.writerow([f"Enrollment - {label}", value])

    completion_labels, completed_data, in_progress_data = get_program_completion_stats()
    for label, comp, in_prog in zip(completion_labels, completed_data, in_progress_data):
        writer.writerow([f"Completion - {label} (Completed)", comp])
        writer.writerow([f"Completion - {label} (In Progress)", in_prog])

    avg_completion_labels, avg_completion_data = get_average_program_completion_percentage()
    for label, value in zip(avg_completion_labels, avg_completion_data):
        writer.writerow([f"Avg Completion - {label}", value])

    return response

def export_user_statistics_csv(request):
    """Generate a CSV report of user statistics."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_statistics.csv"'

    writer = csv.writer(response)
    writer.writerow(["Statistic", "Value"])

    # Fetch statistics
    total_users = EndUser.objects.count()
    active_users = EndUser.objects.filter(user__is_active=True).count()
    inactive_users = total_users - active_users
    total_programs_enrolled = UserProgramEnrollment.objects.count()

    # Get gender distribution
    gender_counts = dict(Counter(EndUser.objects.values_list('gender', flat=True)))
    
    # Get ethnicity distribution
    ethnicity_counts = dict(Counter(EndUser.objects.values_list('ethnicity', flat=True)))
    
    # Get sector distribution
    sector_counts = dict(Counter(EndUser.objects.values_list('sector', flat=True)))

    # Writing the statistics to the CSV file
    writer.writerow(["Total Users", total_users])
    writer.writerow(["Active Users", active_users])
    writer.writerow(["Inactive Users", inactive_users])
    writer.writerow(["Total Programs Enrolled", total_programs_enrolled])

    # Gender distribution
    for gender, count in gender_counts.items():
        writer.writerow([f"Gender - {gender}", count])

    # Ethnicity distribution
    for ethnicity, count in ethnicity_counts.items():
        writer.writerow([f"Ethnicity - {ethnicity}", count])

    # Sector distribution
    for sector, count in sector_counts.items():
        writer.writerow([f"Sector - {sector}", count])

    return response

# Client Modules Views

def module_overview(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "client/moduleOverview.html", {"module": module})

def client_modules(request):
    modules = Module.objects.all().values("id", "title", "description") 
    module_colors = ["color1", "color2", "color3", "color4", "color5", "color6"]
    
    modules_list = []
    for index, module in enumerate(modules):
        module_data = {
            "id": module["id"],
            "title": module["title"],
            "description": module["description"],  
            "color_class": module_colors[index % len(module_colors)]
        }
        modules_list.append(module_data)

    return render(request, "client/client_modules.html", {"modules": modules_list})


# def edit_module(request, module_id):
#     module = get_object_or_404(Module, id=module_id)
    
#     if request.method == "POST":
#         form = ModuleForm(request.POST, instance=module)
#         if form.is_valid():
#             form.save()
#             return redirect('client_modules')  # Redirect back to module management
    
#     else:
#         form = ModuleForm(instance=module)

#     return render(request, 'client/edit_module.html', {'form': form, 'module': module})

def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.delete()
    return redirect("client_modules")


# def add_module(request):
#     if request.method == "POST":
#         title = request.POST.get("title")
#         description = request.POST.get("description")
        
#         if title and description:  # Ensure both fields are filled
#             new_module = Module.objects.create(title=title, description=description)
#             new_module.save()
#             return redirect("client_modules")  # Redirect to the Client Modules page
#     return render(request, "client/add_module.html")

