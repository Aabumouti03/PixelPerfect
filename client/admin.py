from django.contrib import admin
from .models import (
    Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource,
    Category, ProgramModule, BackgroundStyle, ModuleRating, Questionnaire, Question,
    Questionnaire, Question, ProgramModule, Category, BackgroundStyle    
)


class ProgramModuleInline(admin.TabularInline):
    model = ProgramModule
    extra = 1  # Allows adding modules inline
    ordering = ['order']  # Ensures modules appear in correct order
    autocomplete_fields = ['module']  # Enables search for modules
    fields = ('module', 'order')  # Display only relevant fields


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)
    inlines = [ProgramModuleInline]  # 🔹 ADDED: Allows managing module order within a program
    filter_horizontal = ('categories',)  # Allow selection of multiple modules/categories


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'average_rating')
    search_fields = ('title', 'description')
    ordering = ('title',)
    filter_horizontal = ('sections', 'categories', 'additional_resources')

    def average_rating(self, obj):
        """Calculate the average rating of the module."""
        return obj.average_rating()
    
    average_rating.short_description = "Avg Rating"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'diagram_preview', 'text_position_from_diagram')
    search_fields = ('title', 'description')
    ordering = ('title',)
    list_filter = ('text_position_from_diagram',)
    readonly_fields = ('diagram_preview',)

    def diagram_preview(self, obj):
        if obj.diagram:
            return f"✅ Diagram Uploaded"
        return "❌ No Diagram"
    
    diagram_preview.short_description = "Diagram"


@admin.register(AdditionalResource)
class AdditionalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'file_or_url', 'status')
    list_filter = ('resource_type', 'status')
    search_fields = ('title', 'description')

    def file_or_url(self, obj):
        """Show if a file or link is available."""
        if obj.file:
            return "📄 File Uploaded"
        if obj.url:
            return "🔗 URL Provided"
        return "❌ No Resource"
    
    file_or_url.short_description = "Resource"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'exercise_type', 'question_count', 'status')
    list_filter = ('exercise_type', 'status')
    search_fields = ('title',)
    filter_horizontal = ('questions',)

    def question_count(self, obj):
        """Count number of questions in an exercise."""
        return obj.questions.count()
    
    question_count.short_description = "Number of Questions"


@admin.register(ExerciseQuestion)
class ExerciseQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'has_blank', 'question_preview')
    list_filter = ('has_blank',)
    search_fields = ('question_text',)
    fieldsets = (
        (None, {'fields': ('question_text',)}),
        ('Fill-in-the-Blanks', {'fields': ('has_blank', 'text_before_blank', 'text_after_blank')}),  
    )

    def question_preview(self, obj):
        """Preview the question format."""
        if obj.has_blank:
            return f"{obj.text_before_blank} ____ {obj.text_after_blank}"
        return obj.question_text
    
    question_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ProgramModule)
class ProgramModuleAdmin(admin.ModelAdmin):
    list_display = ('program', 'module', 'order')
    list_filter = ('program',)
    ordering = ('program', 'order')


@admin.register(BackgroundStyle)
class BackgroundStyleAdmin(admin.ModelAdmin):
    list_display = ('background_color', 'background_image')
    list_filter = ('background_image',)


@admin.register(ModuleRating)
class ModuleRatingAdmin(admin.ModelAdmin):
    list_display = ('module', 'user', 'rating')
    list_filter = ('module', 'rating')
    ordering = ('module', '-rating')


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'question_text', 'question_type', 'category', 'sentiment')
    list_filter = ('questionnaire', 'question_type', 'category', 'sentiment')
    search_fields = ('question_text',)
