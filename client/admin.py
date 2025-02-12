# from django.contrib import admin
# from .models import Program, Module

# @admin.register(Program)
# class ProgramAdmin(admin.ModelAdmin):
#     list_display = ('id', 'get_modules')  # Show Program ID and related modules
#     filter_horizontal = ('modules',)  # Enables a ManyToMany selection widget
#     search_fields = ('modules__title',)  # Enable search by module title

#     def get_modules(self, obj):
#         """Display associated modules in the admin panel."""
#         return ", ".join(module.title for module in obj.modules.all())
#     get_modules.short_description = 'Modules'

# @admin.register(Module)
# class ModuleAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title')  # Show Module ID and title
#     search_fields = ('title',)  # Enable search by module title
