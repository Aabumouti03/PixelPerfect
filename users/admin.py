from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Admin, EndUser, UserProgramProgress, UserModuleProgress, 
    UserProgramEnrollment, UserModuleEnrollment, UserResponse, 
    Questionnaire_UserResponse, QuestionResponse, StickyNote  # ✅ Updated model name
)
from client.models import Program, Module


@admin.register(Questionnaire_UserResponse)
class QuestionnaireUserResponseAdmin(admin.ModelAdmin):
    """Admin panel for managing user responses to questionnaires."""
    list_display = ('user', 'questionnaire', 'started_at', 'completed_at')
    search_fields = ('user__username', 'questionnaire__title')
    list_filter = ('questionnaire', 'completed_at')
    ordering = ('-started_at',)


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    """Admin panel for managing user responses to individual questions."""
    list_display = ('user_response', 'question', 'rating_value')
    search_fields = ('user_response__user__username', 'question__questionnaire__title', 'question__question_type')
    list_filter = ('question__question_type',)
    ordering = ('user_response',)


# ✅ Your existing admin classes remain unchanged  
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin panel for managing users."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('last_name', 'first_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),  
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),  
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    """Admin panel for managing Admin profiles."""
    list_display = ('user',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')


@admin.register(EndUser)
class EndUserAdmin(admin.ModelAdmin):
    """Admin panel for managing EndUser profiles."""
    list_display = ('user', 'age', 'gender', 'ethnicity', 'sector', 'phone_number')
    list_filter = ('gender', 'ethnicity', 'sector')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number')
    ordering = ('user__last_name', 'user__first_name')


@admin.register(UserProgramEnrollment)
class UserProgramEnrollmentAdmin(admin.ModelAdmin):
    """Admin panel for tracking user enrollments in programs."""
    list_display = ('user', 'program', 'enrolled_on')
    search_fields = ('user__user__username', 'program__title')
    list_filter = ('program',)
    ordering = ('-enrolled_on',)


@admin.register(UserModuleEnrollment)
class UserModuleEnrollmentAdmin(admin.ModelAdmin):
    """Admin panel for tracking user enrollments in standalone modules."""
    list_display = ('user', 'module', 'enrolled_on')
    search_fields = ('user__user__username', 'module__title')
    list_filter = ('module',)
    ordering = ('-enrolled_on',)


@admin.register(UserProgramProgress)
class UserProgramProgressAdmin(admin.ModelAdmin):
    """Admin panel for tracking program progress."""
    list_display = ('user', 'program', 'completion_percentage', 'status', 'last_updated')
    list_filter = ('status',)
    search_fields = ('user__user__username', 'user__user__email', 'program__title')
    ordering = ('user__user__last_name', 'user__user__first_name')


@admin.register(UserModuleProgress)
class UserModuleProgressAdmin(admin.ModelAdmin):
    """Admin panel for tracking module progress."""
    list_display = ('user', 'module', 'completion_percentage', 'status', 'last_updated')
    list_filter = ('status',)
    search_fields = ('user__user__username', 'user__user__email', 'module__title')
    ordering = ('user__user__last_name', 'user__user__first_name')


@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "response_text")
    search_fields = ("user__user__username", "question__question_text")

    def get_form(self, request, obj=None, **kwargs):
        """Ensure all EndUsers appear in the admin dropdown."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].queryset = EndUser.objects.all()  
        return form
    
@admin.register(StickyNote)
class StickyNoteAdmin(admin.ModelAdmin):
    """Admin panel for managing sticky notes."""
    list_display = ('user', 'content', 'created_at', 'updated_at')  # Adjust the fields as needed
    search_fields = ('user__username', 'content')  # Allow searching by the username and content
    list_filter = ('created_at', 'user')  # Optionally filter by created_at and user
    ordering = ('-created_at',)  # Optionally order by created_at in descending order

    def get_form(self, request, obj=None, **kwargs):
        """Ensure all EndUsers appear in the admin dropdown for StickyNote."""
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].queryset = EndUser.objects.all()  # Customize queryset for 'user' field
        return form