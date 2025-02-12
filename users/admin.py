# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from .models import User, Admin, EndUser
# from client.models import Program, Module

# # ✅ Check if model is already registered to avoid duplicate registration
# def is_model_registered(model):
#     return model in admin.site._registry

# # ✅ Ensure Program & Module are registered before being used in `autocomplete_fields`
# if not is_model_registered(Program):
#     @admin.register(Program)
#     class ProgramAdmin(admin.ModelAdmin):
#         search_fields = ['title']  # Adjust based on your model fields

# if not is_model_registered(Module):
#     @admin.register(Module)
#     class ModuleAdmin(admin.ModelAdmin):
#         search_fields = ['title']  # Adjust based on your model fields

# # ✅ Custom User Admin
# if not is_model_registered(User):
#     @admin.register(User)
#     class UserAdmin(BaseUserAdmin):
#         fieldsets = (
#             (None, {'fields': ('username', 'password')}),
#             ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#             ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
#             ('Important dates', {'fields': ('last_login', 'date_joined')}),
#         )

#         add_fieldsets = (
#             (None, {
#                 'classes': ('wide',),
#                 'fields': ('username', 'email', 'password1', 'password2'),
#             }),
#         )

#         list_display = ('username', 'email', 'full_name', 'is_active', 'is_staff')
#         search_fields = ('username', 'email', 'first_name', 'last_name')
#         ordering = ('last_name', 'first_name')

#         def full_name(self, obj):
#             return obj.full_name()
#         full_name.short_description = 'Full Name'


# # ✅ Admin Profile Management
# if not is_model_registered(Admin):
#     @admin.register(Admin)
#     class AdminProfileAdmin(admin.ModelAdmin):
#         list_display = ('id', 'user', 'user_email')
#         search_fields = ('user__username', 'user__email')

#         def user_email(self, obj):
#             return obj.user.email
#         user_email.short_description = 'Email'


# # ✅ EndUser Management
# if not is_model_registered(EndUser):
#     @admin.register(EndUser)
#     class EndUserAdmin(admin.ModelAdmin):
#         list_display = ('id', 'user', 'program', 'module', 'sector', 'age')
#         list_filter = ('program', 'module', 'sector', 'gender')
#         search_fields = ('user__username', 'user__email', 'program__title', 'module__title', 'sector')
#         autocomplete_fields = ['user', 'program', 'module'] 
