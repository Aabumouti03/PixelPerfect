from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Admin, EndUser, UserProgramProgress, UserModuleProgress,UserProgramEnrollment, UserModuleEnrollment ,ExerciseResponse
from client.models import Program, Module

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

@admin.register(ExerciseResponse)
class ExerciseResponseAdmin(admin.ModelAdmin):
    """Admin panel for managing User Responses."""
    list_display = ('user', 'question', 'response_text')
    list_filter = ('user',)
    search_fields = ('user__user__username', 'question__question_text', 'response_text')
    ordering = ('user',)
