from django.contrib import admin
from .models import User, Admin, EndUser, UserResponse

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin panel for managing users."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('last_name', 'first_name')

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

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    """Admin panel for managing User Responses."""
    list_display = ('user', 'question', 'response_text')
    list_filter = ('user',)
    search_fields = ('user__user__username', 'question__question_text', 'response_text')
    ordering = ('user',)
