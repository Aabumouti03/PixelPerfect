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
from client import reports_views as reports_views


urlpatterns = [

    # Users Views
    path('admin/', admin.site.urls),
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
    path('programs/<int:program_id>/delete/', clientViews.delete_program, name='delete_program'),
    path('reports/', reports_views.reports, name='reports'),
    path('userStatistics/', reports_views.userStatistics, name='userStatistics'),    
    path('modules_statistics/', reports_views.modules_statistics, name='modules_statistics'),
    path('programs_statistics/', reports_views.programs_statistics, name='programs_statistics'),
    path('export/modules_statistics/', reports_views.export_modules_statistics_csv, name='export_modules_statistics_csv'),
    path('export/programs_statistics/', reports_views.export_programs_statistics_csv, name='export_programs_statistics_csv'),
    path('category_list/', clientViews.category_list, name='category_list'),  
    path('category/<int:category_id>/', clientViews.category_detail, name='category_detail'),  
    path('create_category/', clientViews.create_category, name='create_category'),


    path('export/users_statistics/', reports_views.export_user_statistics_csv, name='export_user_statistics_csv'),
    
]