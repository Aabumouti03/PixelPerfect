from django.contrib import admin
from .models import Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'diagram_preview', 'text_position_from_diagram')
    search_fields = ('title', 'description')
    ordering = ('title',)
    list_filter = ('text_position_from_diagram',)  
    filter_horizontal = ('additional_resources',)  # ✅ Allow multiple resources
    readonly_fields = ('diagram_preview',)  

    def diagram_preview(self, obj):
        """Show preview if a diagram is uploaded."""
        if obj.diagram:
            return f"✅ Diagram Uploaded"
        return "❌ No Diagram"
    
    diagram_preview.short_description = "Diagram"


@admin.register(AdditionalResource)
class AdditionalResourceAdmin(admin.ModelAdmin):
    """Admin panel for Additional Resources like books, podcasts, surveys, and PDFs."""
    list_display = ('title', 'resource_type', 'file_or_url')
    list_filter = ('resource_type',)
    search_fields = ('title', 'description')

    def file_or_url(self, obj):
        """Show a file or link if available."""
        if obj.file:
            return f"📄 File Uploaded"
        if obj.url:
            return f"🔗 URL Provided"
        return "❌ No Resource"
    
    file_or_url.short_description = "Resource"


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'exercise_type', 'question_count')  
    list_filter = ('exercise_type',)
    search_fields = ('title',)
    filter_horizontal = ('questions',)  

    def question_count(self, obj):
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
        if obj.has_blank:
            return f"{obj.text_before_blank} ____ {obj.text_after_blank}"
        return obj.question_text
    
    question_preview.short_description = "Preview"
