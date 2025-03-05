from django.shortcuts import render, redirect, get_object_or_404
from client.models import Program, Module
from django.shortcuts import render, get_object_or_404
from client.models import Module
from .forms import ModuleForm, SectionForm, ExerciseForm, QuestionForm
from .models import Module, Section, Exercise, Question


def CreateModule(request):
    modules = Module.objects.prefetch_related("sections__exercises__questions").all()
    return render(request, "Module/Edit_Add_Module.html", {"modules": modules})

def EditModule(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    return render(request, "Module/edit_module.html", {"module": module})

def AddModule(request):
    if request.method == 'POST':
        module_form = ModuleForm(request.POST)
        
        if module_form.is_valid():
            module = module_form.save()

            # Processing sections
            sections_data = request.POST.getlist('section_title')  # Correct field name
            for section_title in sections_data:
                if section_title.strip():  # Ensure it's not empty
                    section = Section.objects.create(title=section_title)
                    module.sections.add(section)  # Correctly link Section to Module

                    # Processing exercises for each section
                    exercises_data = request.POST.getlist(f'exercise_title_{section_title}')
                    for exercise_title in exercises_data:
                        if exercise_title.strip():
                            exercise = Exercise.objects.create(title=exercise_title)
                            section.exercises.add(exercise)  # Correctly link Exercise to Section

                            # Processing questions for each exercise
                            questions_data = request.POST.getlist(f'question_text_{exercise_title}')
                            for question_text in questions_data:
                                if question_text.strip():
                                    question = Question.objects.create(question_text=question_text)
                                    exercise.questions.add(question)  # Correctly link Question to Exercise

            return redirect('edit_add_module')  

    else:
        module_form = ModuleForm()

    return render(request, 'Module/add_module.html', {'module_form': module_form})


def programs(request):
    return render(request, 'client/programs.html')

def logout_view(request):
    return render(request, 'client/logout.html')

def client_dashboard(request):
    return render(request, 'client/client_dashboard.html')

def users_management(request):
    users = User.objects.all().select_related('User_profile')
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
