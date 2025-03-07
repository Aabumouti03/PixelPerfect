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
from client import views as client_views
from users import views as usersViews
from django.contrib.auth import views as authenticationViews



urlpatterns = [

    #Admin url
    path('admin/', admin.site.urls),

    #Authentication
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.log_out, name="log_out"),
    path('sign-up/', usersViews.sign_up_step_1, name='sign_up_step_1'),
    path('sign-up/profile/', usersViews.sign_up_step_2, name='sign_up_step_2'),
    path('log_out_client/', clientViews.log_out_client, name="log_out_client"),
    path('reset_password/', 
        authenticationViews.PasswordResetView.as_view(template_name="users/reset_password.html"),
        name="reset_password"),
    path('reset_password_sent/',
        authenticationViews.PasswordResetDoneView.as_view(template_name="users/password_reset_sent.html"),
        name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
        authenticationViews.PasswordResetConfirmView.as_view(template_name="users/password_reset_form.html"),
        name="password_reset_confirm"),
    path('reset_password_complete/',
        authenticationViews.PasswordResetCompleteView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_complete"),

    #Welcome Page
    path('about/', usersViews.about, name='about'),
    path('', usersViews.welcome_page, name="welcome_page"),
    path('contact_us/', usersViews.contact_us, name='contact_us'),

    #Program urls for the client
    path('programs/', clientViews.programs, name='programs'),
    path('create_program/', clientViews.create_program, name='create_program'),
    path('programs/<int:program_id>/', clientViews.program_detail, name='program_detail'),
    path('programs/<int:program_id>/delete/', clientViews.delete_program, name='delete_program'),
    path('programs/<int:program_id>/update_order/', clientViews.update_module_order, name="update_module_order"),

    #Dashboard details for the client
    path('users_management/', clientViews.users_management, name='users_management'),
    path('modules_management/', clientViews.modules_management, name='modules_management'),
    path('client_dashboard/', clientViews.client_dashboard, name='client_dashboard'),
    path('users_management/', clientViews.users_management, name='users_management'),

    #User urls for modules
    path('userModules/', usersViews.user_modules, name='userModules'),
    path('module_overview/<int:id>/', usersViews.module_overview, name='module_overview'),
    path('all_modules/', usersViews.all_modules, name='all_modules'),

    # User dashboard details
    path('dashboard/', usersViews.dashboard, name='dashboard'),
    path('profile/', usersViews.profile, name='profile'),
    path('reports/', clientViews.reports, name='reports'),
    path('userStatistics/', clientViews.userStatistics, name='userStatistics'),    
    path('modules_statistics/', clientViews.modules_statistics, name='modules_statistics'),
    path('programs_statistics/', clientViews.programs_statistics, name='programs_statistics'),
    path('export/modules_statistics/', clientViews.export_modules_statistics_csv, name='export_modules_statistics_csv'),
    path('export/programs_statistics/', clientViews.export_programs_statistics_csv, name='export_programs_statistics_csv'),
    path('category_list/', clientViews.category_list, name='category_list'),  
    path('category/<int:category_id>/', clientViews.category_detail, name='category_detail'),  
    path('create_category/', clientViews.create_category, name='create_category'),


    path('export/users_statistics/', clientViews.export_user_statistics_csv, name='export_user_statistics_csv'),
    
]