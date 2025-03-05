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

            # Process sections
            sections_data = request.POST.getlist('sections[0][title]')  # Extract section titles
            section_counter = 0

            while f'sections[{section_counter}][title]' in request.POST:
                section_title = request.POST[f'sections[{section_counter}][title]']
                if section_title.strip():
                    section = Section.objects.create(title=section_title)
                    module.sections.add(section)  # Link section to module

                    # Process exercises
                    exercise_counter = 0
                    while f'sections[{section_counter}][exercises][{exercise_counter}][title]' in request.POST:
                        exercise_title = request.POST[f'sections[{section_counter}][exercises][{exercise_counter}][title]']
                        if exercise_title.strip():
                            exercise = Exercise.objects.create(title=exercise_title)
                            section.exercises.add(exercise)  # Link exercise to section

                            # Process questions
                            question_counter = 0
                            while f'sections[{section_counter}][exercises][{exercise_counter}][questions][{question_counter}][text]' in request.POST:
                                question_text = request.POST[f'sections[{section_counter}][exercises][{exercise_counter}][questions][{question_counter}][text]']
                                if question_text.strip():
                                    question = Question.objects.create(question_text=question_text)
                                    exercise.questions.add(question)  # Link question to exercise
                                question_counter += 1
                        exercise_counter += 1
                section_counter += 1

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
