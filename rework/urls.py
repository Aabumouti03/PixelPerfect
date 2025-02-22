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
from users.views.users import logViews as logViews
from users.views.users import module_views as user_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    # Users Views
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('', logViews.welcome_page, name="welcome_page"),
    path('log_in/', logViews.log_in, name="log_in"),
    path('log_out/', logViews.log_out, name="log_out"),
    path('sign-up/', logViews.sign_up_step_1, name='sign_up_step_1'),
    path('sign-up/profile/', logViews.sign_up_step_2, name='sign_up_step_2'),
    path('dashboard/', logViews.dashboard, name='dashboard'),
    path('modules/', logViews.modules, name='modules'),
    path('profile/', logViews.profile, name='profile'),
    path('about/', logViews.about, name='about'),
    path('contact_us/', logViews.contact_us, name='contact_us'),
    path('module/<int:module_id>/', user_views.module_overview, name='module_overview'),
    path('exercise/<int:exercise_id>/', user_views.exercise_detail, name='exercise_detail'),

]

# insures that media content is accesisble via URLs
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
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
>>>>>>> origin/create_programs
