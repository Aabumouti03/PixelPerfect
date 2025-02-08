from django.contrib import admin
from .models import Program, Module, Questionnaire, Question, QuestionOption, Option

# Inline for Options (within QuestionOption)
class OptionInline(admin.TabularInline):
    model = Option
    extra = 1  # Number of empty forms to display in the admin interface
    autocomplete_fields = ['question_option']

# Inline for QuestionOption (within Question)
class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 1
    inlines = [OptionInline]

# Admin for Program
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_modules')
    filter_horizontal = ('modules',)  # Adds a widget for managing ManyToMany fields
    search_fields = ('modules__title',)  # Enable search by module title

    def get_modules(self, obj):
        """Display associated modules in the admin list."""
        return ", ".join(module.title for module in obj.modules.all())
    get_modules.short_description = 'Modules'

# Admin for Module
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

# Admin for Questionnaire
@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_questions')
    search_fields = ('title', 'questions__question_text')

    def get_questions(self, obj):
        """Display associated questions in the admin list."""
        return ", ".join(question.question_text for question in obj.questions.all())
    get_questions.short_description = 'Questions'

# Admin for Question
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'type', 'has_options')
    search_fields = ('question_text',)
    list_filter = ('type',)
    inlines = [QuestionOptionInline]

    def has_options(self, obj):
        """Check if the question has options."""
        return obj.option_set is not None
    has_options.boolean = True
    has_options.short_description = 'Has Options'

# Admin for QuestionOption
@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'get_options')
    search_fields = ('question__question_text',)

    def get_options(self, obj):
        """Display associated options in the admin list."""
        return ", ".join(option.option_text for option in obj.options.all())
    get_options.short_description = 'Options'

# Admin for Option
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('option_text', 'question_option')
    search_fields = ('option_text', 'question_option__question__question_text')
