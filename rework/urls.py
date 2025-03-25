from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from client import views as clientViews
from users import views as usersViews
from django.contrib.auth import views as authenticationViews



urlpatterns = [

    # Admin url
    path('admin/', admin.site.urls),
  
    # Home and dashboard section
    path('', usersViews.welcome_page, name="welcome_page"),
    path('dashboard/', usersViews.dashboard, name="dashboard"),
    path('about/', usersViews.about, name='about'),
    path('contact_us/', usersViews.contact_us, name='contact_us'),
    path('contact-success/', usersViews.contact_success, name='contact_success'),
    path("get_started/", usersViews.get_started, name="get_started"),
    path('client_dashboard/', clientViews.client_dashboard, name='client_dashboard'),

    # Authentication urls
    path('log_in/', usersViews.log_in, name="log_in"),
    path('log_out/', usersViews.log_out, name="log_out"),
    path('log_out/', clientViews.log_out_client, name="log_out"),
    path('verification_done/', usersViews.verification_done, name="verification_done"),
    path('sign-up/', usersViews.sign_up_step_1, name='sign_up_step_1'),
    path('sign-up/profile/', usersViews.sign_up_step_2, name='sign_up_step_2'),
    path('log_out_client/', clientViews.log_out_client, name="log_out_client"),
    path('sign_up_email_verification/', usersViews.sign_up_email_verification, name="sign_up_email_verification"),
    path('verify-email-after-sign-up/<uidb64>/<token>/', usersViews.verify_email_after_sign_up, name='verify_email_after_sign_up'),
    path('reset_password/', 
        authenticationViews.PasswordResetView.as_view(template_name="users/password_reset_form.html"),
        name="password_reset_form"),
    path('reset_password_sent/',
        authenticationViews.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
        authenticationViews.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm"),
    path('reset_password_complete/',
        authenticationViews.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete"),


    # Modules (Client)
    path("modules/create/", clientViews.createModule, name="add_module"),
    path('edit_module/<int:module_id>/', clientViews.edit_module, name='edit_module'),
    path('edit_section/<int:section_id>/', clientViews.edit_section, name='edit_section'),
    path('edit_exercise/<int:exercise_id>/', clientViews.edit_exercise, name='edit_exercise'),
    path('update_module/<int:module_id>/', clientViews.update_module, name='update_module'),
    path('add_section_to_module/<int:module_id>/', clientViews.add_section_to_module, name='add_section_to_module'),
    path('remove_section_from_module/<int:module_id>/', clientViews.remove_section_from_module, name='remove_section_from_module'),
    path('update_section/<int:section_id>/', clientViews.update_section, name='update_section'), 
    path('add_exercise_to_section/<int:section_id>/', clientViews.add_exercise_to_section, name='add_exercise_to_section'),
    path('remove_exercise_from_section/<int:section_id>/', clientViews.remove_exercise_from_section, name='remove_exercise_from_section'),
    path('manage_exercises/', clientViews.manage_exercises, name='manage_exercises'),
    path('update_exercise/<int:exercise_id>/', clientViews.update_exercise, name='update_exercise'),
    path('delete_exercise_questions/<int:exercise_id>/', clientViews.delete_exercise_questions, name='delete_exercise_questions'),
    path("add_exercise_ajax/", clientViews.add_exercise_ajax, name="add_exercise_ajax"),
    path('add_exercise_to_module/<int:module_id>/', clientViews.add_exercise_to_module, name='add_exercise_to_module'),
    path('remove_video_from_module/<int:module_id>/', clientViews.remove_video_from_module, name='remove_video_from_module'),
    path('remove_exercises_from_module/<int:module_id>/', clientViews.remove_exercise_from_module, name='remove_exercises_from_module'),
    path('delete_video/<int:video_id>/', clientViews.delete_video, name='delete_video'),
    path("client_modules/", clientViews.client_modules, name="client_modules"),
    path('edit_module/<int:module_id>/', clientViews.edit_module, name='edit_module'),  
    path("delete_module/<int:module_id>/", clientViews.delete_module, name="delete_module"),
    path('add_video_to_module/<int:module_id>/', clientViews.add_video_to_module, name='add_video_to_module'),

    #Resources urls for the client
    path('add_additional_resource/', clientViews.add_additional_resource, name='add_additional_resource'),
    path('remove_resource_from_module/<int:module_id>/', clientViews.remove_resource_from_module, name='remove_resource_from_module'),
    path('resource_list/', clientViews.resource_list, name='resource_list'),
    path('delete_resource/<int:resource_id>/', clientViews.delete_resource, name='delete_resource'),
    path('add_resource_to_module/<int:module_id>/', clientViews.add_resource_to_module, name='add_resource_to_module'),
    path('save_module_changes/<int:module_id>/', clientViews.save_module_changes, name='save_module_changes'),
    

    #Additional Section and Exercise urls
    path('sections/add/', clientViews.add_section, name='add_section'),
    path('sections/get_all/', clientViews.get_sections, name='get_sections'),
    path('exercises/add/', clientViews.add_exercise, name='add_exercise'), 
    path('questions/add/', clientViews.add_Equestion, name='add_question'),  

    # Profile management
    path('profile/', usersViews.profile, name='profile'),  
    path('profile/edit/', usersViews.update_profile, name='update_profile'),  
    path('profile/delete/', usersViews.delete_account, name='delete_account'),
    path('verify-email/<uidb64>/<token>/', usersViews.verify_email, name='verify_email'),

    # Program urls for the client
    path('programs/', clientViews.programs, name='programs'),
    path('create_program/', clientViews.create_program, name='create_program'),
    path('create_program/', clientViews.create_program, name='create_program'),
    path('programs/<int:program_id>/', clientViews.program_detail, name='program_detail'),
    path('programs/<int:program_id>/delete/', clientViews.delete_program, name='delete_program'),
    path('programs/<int:program_id>/update_order/', clientViews.update_module_order, name="update_module_order"),

    # User management section for the client
    path('users_management/', clientViews.users_management, name='users_management'),
    
    # Categories section for the client
    path('create_category/', clientViews.create_category, name='create_category'),
    path('category_list/', clientViews.category_list, name='category_list'),  
    path('category/<int:category_id>/', clientViews.category_detail, name='category_detail'), 
    path('categories/<int:category_id>/edit/', clientViews.edit_category, name='edit_category'),   

    # Module urls for the users
    path('userModules/', usersViews.user_modules, name='modules'),
    path('module_overview/<int:module_id>/', usersViews.module_overview, name='module_overview'),
    path('userResponce/', usersViews.user_responses_main, name='userResponce'),
    path('userModules/', usersViews.user_modules, name='userModules'),
    path('module/<int:module_id>/', usersViews.module_overview, name='module_overview'),
    path('module/<int:module_id>/rate/', usersViews.rate_module, name='rate_module'),
    path('exercise/<int:exercise_id>/', usersViews.exercise_detail, name='exercise_detail'),
    path('exercise/<int:exercise_id>/view/', usersViews.exercise_detail_view, name='exercise_detail_view'),
    path('mark_done/', usersViews.mark_done, name='mark_done'),
    path('all_modules/', usersViews.all_modules, name='all_modules'),
    
    # Statistics urls for the clilent
    path('reports/', clientViews.reports, name='reports'),
    path('userStatistics/', clientViews.userStatistics, name='userStatistics'),    
    path('modules_statistics/', clientViews.modules_statistics, name='modules_statistics'),
    path('programs_statistics/', clientViews.programs_statistics, name='programs_statistics'),
    path('export/modules_statistics/', clientViews.export_modules_statistics_csv, name='export_modules_statistics_csv'),
    path('export/programs_statistics/', clientViews.export_programs_statistics_csv, name='export_programs_statistics_csv'),

    # Personalized recommendations for the user
    path("recommended_programs/", usersViews.recommended_programs, name="recommended_programs"),
    path("recommended_modules/", usersViews.recommended_modules, name="recommended_modules"),

    # User dashboard details
    path('save-notes/', usersViews.save_notes, name='save_notes'),
    path('get-notes/', usersViews.get_notes, name='get_notes'), 
    path('program/<int:program_id>/', usersViews.view_program, name='view_program'),

    # Questionnaire
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
    path('manage_questionnaires/activate/<int:questionnaire_id>/', clientViews.activate_questionnaire, name='activate_questionnaire'),

    # Enrollement and Unenrollment modules
    path("enroll-module/", usersViews.enroll_module, name="enroll_module"),
    path("unenroll-module/", usersViews.unenroll_module, name="unenroll_module"), 
    path('module_overview/<int:module_id>/', usersViews.module_overview, name='module_overview'),

    # Video urls for the client
    path('videos/', clientViews.video_list, name='video_list'),
    path('videos/add/', clientViews.add_video, name='add_video'),
    path('videos/<int:video_id>/', clientViews.video_detail, name='video_detail'),

    # Journal urls for the users
    path("journal/", usersViews.journal_view, name="journal_page"),  # Default view (today's date)
    path("journal/<str:date>/", usersViews.journal_view, name="journal_by_date"),  # View by date
    path("save_journal_entry/", usersViews.save_journal_entry, name="save_journal_entry"),
    path("journal/save/", usersViews.save_journal_entry, name="journal_save"),  # Form submission

    # Other
    path('user_response/<int:user_response_id>/', clientViews.view_user_response, name='view_user_response'),
    path('export/users_statistics/', clientViews.export_user_statistics_csv, name='export_user_statistics_csv'),
    path('user/<int:user_id>/', clientViews.user_detail_view, name='user_detail_view'),

]

# Debug settings
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)