from django.contrib import admin
from .models import Program, Module, Section, Exercise, ExerciseQuestion

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin panel for managing Programs."""
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin panel for managing Modules."""
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin panel for managing Sections."""
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """Admin panel for managing Exercises."""
    list_display = ('title', 'exercise_type')
    list_filter = ('exercise_type',)
    search_fields = ('title',)
    filter_horizontal = ('questions',)  
    ordering = ('title',)


@admin.register(ExerciseQuestion)
class ExerciseQuestionAdmin(admin.ModelAdmin):
    """Admin panel for managing Exercise Questions."""
    list_display = ('question_text', 'question_type')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
    ordering = ('question_text',)
