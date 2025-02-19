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
from users.views import logViews as logViews
from users.views import module_views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
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
