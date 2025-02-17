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
<<<<<<< HEAD
=======
from client import views as clientViews
>>>>>>> origin/userAuthentication
from users import views as usersViews

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('log_out/', usersViews.log_out, name='log_out'),

    #profile page add-ons
    path('profile/', usersViews.profile, name='show_profile'),  
    path('profile/edit/', usersViews.update_profile, name='update_profile'),  
    path('profile/delete/', usersViews.delete_account, name='delete_account'),    

]
=======
    path('', usersViews.welcome_page, name="welcome_page"),
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.log_out, name="log_out"),
    path('sign_up/', usersViews.sign_up, name="sign_up"),
    path('dashboard/', usersViews.dashboard, name='dashboard'),
    path('modules/', usersViews.modules, name='modules'),
    path('profile/', usersViews.profile, name='profile'),
]
>>>>>>> origin/userAuthentication
