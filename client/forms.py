from django import forms
from .models import Module, Section, Exercise, Question

class ModuleForm(forms.ModelForm):
    sections = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # ✅ Change to checkboxes
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
    class Meta:
        model = Section
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter section title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter section description', 'rows': 3}),
        }