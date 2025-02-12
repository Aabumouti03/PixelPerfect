from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Admin, EndUser

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
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
