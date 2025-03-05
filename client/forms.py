from django import forms
from .models import Module, Section, Exercise, Question

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']
        widgets = {
            'question_text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question...'})
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter exercise title...'})
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter section title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter section description...', 'rows': 2})
        }


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter module title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter module description...', 'rows': 3})
        }
