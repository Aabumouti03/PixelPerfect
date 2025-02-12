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
from client import views as client_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', user_views.dashboard, name='dashboard'),
    path('modules/', user_views.modules, name='modules'),
    path('profile/', user_views.profile, name='profile'),
    path('logout/', user_views.logout_view, name='logout'),
    path('moduleOverview/', client_views.module_overview, name='module_overview'),
]
