from django.contrib import admin
from .models import (
    Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource,  
    Questionnaire, Question, ProgramModule, Category, BackgroundStyle  
)


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('is_active',)
    ordering = ('-created_at',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('questionnaire', 'question_text', 'question_type', 'is_required')
    search_fields = ('questionnaire__title',)
    list_filter = ('question_type', 'is_required')
    ordering = ('questionnaire',)

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




@admin.register(Category)  # 🔹 ADDED: To manage categories in Django Admin
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


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


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'background_style')  
    search_fields = ('title', 'description')
    ordering = ('title',)
    filter_horizontal = ('additional_resources',) 
    autocomplete_fields = ('background_style',) 

@admin.register(AdditionalResource)
class AdditionalResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'file_or_url')
    list_filter = ('resource_type',)
    search_fields = ('title', 'description')

    def file_or_url(self, obj):
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


@admin.register(ProgramModule)
class ProgramModuleAdmin(admin.ModelAdmin):
    list_display = ('program', 'module', 'order')
    ordering = ('program', 'order')
    autocomplete_fields = ('program', 'module')  # Enables search dropdown

@admin.register(BackgroundStyle)
class BackgroundStyleAdmin(admin.ModelAdmin):
    list_display = ('background_color', 'background_image')
    search_fields = ('background_color', 'background_image')
    list_filter = ('background_color',)