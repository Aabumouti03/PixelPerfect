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
from client import views
from users import views as usersViews
from client.views import delete_module
from users.views import enroll_module, unenroll_module 


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', usersViews.welcome_page, name="welcome_page"),
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.logout_view, name="log_out"),

    path('sign_up/', usersViews.sign_up, name="sign_up"),
    path('dashboard/', usersViews.dashboard, name='dashboard'),
     path("enroll-module/", enroll_module, name="enroll_module"),
    path("unenroll-module/", unenroll_module, name="unenroll_module"), 
    path('userModules/', usersViews.user_modules, name='userModules'),
    path('module_overview/<int:module_id>/', usersViews.module_overview, name='module_overview'),
    path('all_modules/', usersViews.all_modules, name='all_modules'),
    path('profile/', usersViews.profile, name='profile'),

    # Client URLs
    
    path('users_management/', clientViews.users_management, name='users_management'),
    path("client_modules/", views.client_modules, name="client_modules"),
    path('edit_module/<int:module_id>/', clientViews.edit_module, name='edit_module'),  
    path('add_module/', views.add_module, name='add_module'),
    path("delete_module/<int:module_id>/", delete_module, name="delete_module"),
    path('client_dashboard/', clientViews.client_dashboard, name='client_dashboard'),
    path('programs/', clientViews.programs, name='programs'),
    path('create_program/', clientViews.create_program, name='create_program'),
    path('programs/<int:program_id>/', clientViews.program_detail, name='program_detail'),
    path('programs/<int:program_id>/delete/', clientViews.delete_program, name='delete_program'),
    
]