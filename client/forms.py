from django import forms
from .models import Module, Section, Exercise, Question, ExerciseQuestion


class ModuleForm(forms.ModelForm):
    sections = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),  # ✅ Show all sections
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Module
        fields = ['title', 'description', 'sections']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter module title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter module description', 'rows': 3}),
        }

class SectionForm(forms.ModelForm):
    exercises = forms.ModelMultipleChoiceField(
        queryset=Exercise.objects.all(),  # ✅ Show all exercises
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Section
        fields = ['title', 'description', 'exercises']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter section title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter section description', 'rows': 3}),
        }

class ExerciseForm(forms.ModelForm):
    questions = forms.ModelMultipleChoiceField(
        queryset=ExerciseQuestion.objects.all(),  # ✅ Show all questions
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Exercise
        fields = ['title', 'exercise_type', 'questions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter exercise title'}),
            'exercise_type': forms.Select(attrs={'class': 'form-control'}),
        }

class ExerciseQuestionForm(forms.ModelForm):
    class Meta:
        model = ExerciseQuestion
        fields = ['question_text', 'has_blank', 'text_before_blank', 'text_after_blank']
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter question text', 'rows': 2}),
            'has_blank': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'text_before_blank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text before blank'}),
            'text_after_blank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Text after blank'}),
        }

