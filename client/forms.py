from django import forms
from .models import Program, Module

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['title', 'description', 'modules']
        widgets = {
            'modules': forms.CheckboxSelectMultiple(),
        }
