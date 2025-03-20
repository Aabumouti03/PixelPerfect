from django.contrib import admin
from .models import (
    Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource,
    Category, ProgramModule, BackgroundStyle, ModuleRating, Questionnaire, Question,
    VideoResource
)


class ProgramModuleInline(admin.TabularInline):
    """Inline admin to manage program modules within a program."""
    model = ProgramModule
    extra = 1
    ordering = ['order']
    autocomplete_fields = ['module']
    fields = ('module', 'order')


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Admin settings for the Program model."""
    list_display = ('title', 'description', 'display_categories')
    search_fields = ('title', 'description')
    ordering = ('title',)
    inlines = [ProgramModuleInline]
    filter_horizontal = ('categories',)

    def display_categories(self, obj):
        """Display categories as a comma-separated list."""
        return ", ".join(category.name for category in obj.categories.all())

    display_categories.short_description = "Categories"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    """Admin settings for the Module model."""
    list_display = ('title', 'description', 'average_rating', 'display_categories')
    search_fields = ('title', 'description')
    ordering = ('title',)
    filter_horizontal = ('sections', 'categories', 'additional_resources')

    def average_rating(self, obj):
        """Calculate the average rating of the module."""
        return obj.average_rating()

    average_rating.short_description = "Avg Rating"

    def display_categories(self, obj):
        """Display categories as a comma-separated list."""
        return ", ".join(category.name for category in obj.categories.all())

    display_categories.short_description = "Categories"


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    """Admin settings for the Section model."""
    list_display = ('title', 'diagram_preview', 'text_position_from_diagram')
    search_fields = ('title', 'description')
    ordering = ('title',)
    list_filter = ('text_position_from_diagram',)
    readonly_fields = ('diagram_preview',)

    def diagram_preview(self, obj):
        """Display a checkmark if a diagram is uploaded."""
        return "✅ Diagram Uploaded" if obj.diagram else "❌ No Diagram"

    diagram_preview.short_description = "Diagram"


@admin.register(AdditionalResource)
class AdditionalResourceAdmin(admin.ModelAdmin):
    """Admin settings for the AdditionalResource model."""
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
    """Admin settings for the Exercise model."""
    list_display = ('title', 'exercise_type', 'question_count', 'status')
    list_filter = ('exercise_type', 'status')
    search_fields = ('title',)
    filter_horizontal = ('questions',)

    def question_count(self, obj):
        """Count the number of questions in an exercise."""
        return obj.questions.count()

    question_count.short_description = "Number of Questions"


@admin.register(ExerciseQuestion)
class ExerciseQuestionAdmin(admin.ModelAdmin):
    """Admin settings for the ExerciseQuestion model."""
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


@admin.register(VideoResource)
class VideoResourceAdmin(admin.ModelAdmin):
    """Admin settings for the VideoResource model."""
    list_display = ('title', 'youtube_url')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin settings for the Category model."""
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ProgramModule)
class ProgramModuleAdmin(admin.ModelAdmin):
    """Admin settings for the ProgramModule model."""
    list_display = ('program', 'module', 'order')
    list_filter = ('program',)
    ordering = ('program', 'order')


@admin.register(BackgroundStyle)
class BackgroundStyleAdmin(admin.ModelAdmin):
    """Admin settings for the BackgroundStyle model."""
    list_display = ('background_color', 'background_image')
    list_filter = ('background_image',)


@admin.register(ModuleRating)
class ModuleRatingAdmin(admin.ModelAdmin):
    """Admin settings for the ModuleRating model."""
    list_display = ('module', 'user', 'rating')
    list_filter = ('module', 'rating')
    ordering = ('module', '-rating')


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    """Admin settings for the Questionnaire model."""
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin settings for the Question model."""
    list_display = ('questionnaire', 'question_text', 'question_type', 'category', 'sentiment')
    list_filter = ('questionnaire', 'question_type', 'category', 'sentiment')
    search_fields = ('question_text',)
