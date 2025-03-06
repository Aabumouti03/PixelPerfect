from django.contrib import admin
from django.urls import path
from client import views
from users import views
from client import views as client_views
from client import views as clientViews
from users import views as usersViews

urlpatterns = [

    # Users Views
    # Admin
    path('admin/', admin.site.urls),

    # Users Views
    path('', usersViews.welcome_page, name="welcome_page"),
    path('dashboard/', usersViews.dashboard, name="dashboard"),

    # Redirect "Modules" to "Edit_Add_Module"
    path('modules/', clientViews.CreateModule, name="modules"),

    path('about/', usersViews.about, name='about'),

    # Other Paths
    path('profile/', usersViews.profile, name='profile'),
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.log_out, name="log_out"),
    path('sign-up/', usersViews.sign_up_step_1, name='sign_up_step_1'),
    path('sign-up/profile/', usersViews.sign_up_step_2, name='sign_up_step_2'),

    # Modules (Client)
    path("modules/edit_add/", clientViews.CreateModule, name="edit_add_module"),
    path("modules/edit/<int:module_id>/", clientViews.EditModule, name="edit_module"),
    # path("modules/add/", clientViews.AddModule, name="add_module"),

    path('userResponce/', usersViews.user_responses_main, name='userResponce'),
    path('modules/', usersViews.modules, name='modules'),
    path('contact_us/', usersViews.contact_us, name='contact_us'),
   
    path('modules/add/', clientViews.add_module, name='add_module'),
    path('sections/add/', clientViews.add_section, name='add_section'),
    path('sections/get_all/', clientViews.get_sections, name='get_sections'),
    
    
]
