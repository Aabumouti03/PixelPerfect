from django.contrib import admin
from .models import Program, Module, Section, Exercise, ExerciseQuestion

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    filter_horizontal = ('modules',)  

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    filter_horizontal = ('sections',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    filter_horizontal = ('exercises',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_sections', 'exercise_type')  
    list_filter = ('exercise_type',)  
    search_fields = ('title',)

    def get_sections(self, obj):
        return ", ".join([section.title for section in obj.sections.all()])
    get_sections.short_description = "Sections"  

@admin.register(ExerciseQuestion)
class ExerciseQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'exercise', 'question_type')
    list_filter = ('question_type',)

# @admin.register(UserResponse)
# class UserResponseAdmin(admin.ModelAdmin):
#     list_display = ('user', 'question', 'response_text')
#     list_filter = ('user',)

