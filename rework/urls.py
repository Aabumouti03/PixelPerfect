"""
URL configuration for rework project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from client import views as clientViews
from users import views as usersViews


urlpatterns = [

    # Users Views
    path('admin/', admin.site.urls),
    path('welcome/', usersViews.welcome_view, name='welcome'),
    path('questionnaire/', usersViews.questionnaire, name='questionnaire'),
    path("submit-responses/", usersViews.submit_responses, name="submit_responses"),
    path('manage_questionnaires/', clientViews.manage_questionnaires, name='manage_questionnaires'),
    path("manage_questionnaires/create_questionnaire/", clientViews.create_questionnaire, name="create_questionnaire"),
    path('manage_questionnaires/<int:questionnaire_id>/', clientViews.view_questionnaire, name='view_questionnaire'),
    path('manage_questionnaires/<int:questionnaire_id>/delete/', clientViews.delete_questionnaire, name='delete_questionnaire'),
    path('manage_questionnaires/<int:questionnaire_id>/responders/', clientViews.view_responders, name='view_responders'),
    path('manage_questionnaires/edit/<int:questionnaire_id>/', clientViews.edit_questionnaire, name='edit_questionnaire'),
    path('manage_questionnaires/delete_question/<int:question_id>/', clientViews.delete_question, name='delete_question'),
    path('manage_questionnaires/add_question/<int:questionnaire_id>/', clientViews.add_question, name='add_question'),
    path('user_response/<int:user_response_id>/', clientViews.view_user_response, name='view_user_response'),
    path('manage_questionnaires/activate/<int:questionnaire_id>/', clientViews.activate_questionnaire, name='activate_questionnaire'),
    path('programs/', clientViews.programs, name='programs'),
    path('logout/', clientViews.logout_view, name='logout'),
    path('', usersViews.welcome_page, name="welcome_page"),
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.log_out, name="log_out"),
    path('sign-up/', usersViews.sign_up_step_1, name='sign_up_step_1'),
    path('sign-up/profile/', usersViews.sign_up_step_2, name='sign_up_step_2'),
    path('dashboard/', usersViews.dashboard, name='dashboard'),
    path('about/', usersViews.about, name='about'),
    path('contact_us/', usersViews.contact_us, name='contact_us'),
    path('userModules/', usersViews.user_modules, name='userModules'),
    path('module_overview/<int:module_id>/', usersViews.module_overview, name='module_overview'),
    path('all_modules/', usersViews.all_modules, name='all_modules'),
    path('profile/', usersViews.profile, name='profile'),
    path('users_management/', clientViews.users_management, name='users_management'),
    path('modules_management/', clientViews.modules_management, name='modules_management'),
    path('client_dashboard/', clientViews.client_dashboard, name='client_dashboard'),
    path('users_management/', clientViews.users_management, name='users_management'),
    path('programs/', clientViews.programs, name='programs'),
    path('log_out/', clientViews.log_out, name="log_out"),
    path('create_program/', clientViews.create_program, name='create_program'),
    path('programs/<int:program_id>/', clientViews.program_detail, name='program_detail'),
    path('programs/<int:program_id>/delete/', clientViews.delete_program, name='delete_program')
]