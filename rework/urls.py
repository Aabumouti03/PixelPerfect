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
from users import views
from client import views as clientViews
from users import views as usersViews
from users.views import enroll_module, unenroll_module 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', usersViews.welcome_page, name="welcome_page"),
    path('log_in/', usersViews.log_in, name="log_in"),
    path('sign_up/', usersViews.sign_up, name="sign_up"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('modules/', views.modules, name='modules'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('module-overview/<int:id>/', views.module_overview, name='module_overview'),
    path("enroll-module/", enroll_module, name="enroll_module"),
    path("unenroll-module/", unenroll_module, name="unenroll_module"),  # ✅ New route
    path('user-modules/', views.user_modules, name='modules'),
    path('all-modules/', views.all_modules, name='all_modules'),

]