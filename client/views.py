from django.shortcuts import render, get_object_or_404
from users.models import User
from client.models import Module
from users.models import EndUser, UserProgramEnrollment, UserModuleEnrollment, Questionnaire_UserResponse, QuestionResponse

# Create your views here.

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
