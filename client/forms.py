from django import forms
from .models import Program, Module

class ProgramForm(forms.ModelForm):
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "module-checkbox"}),
        required=False
    )
    module_order = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Program
        fields = ['title', 'description', 'modules', 'module_order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-pill border-2', 
                'placeholder': 'Enter program title:'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control rounded-pill border-2',
                'rows': 3,
                'placeholder': 'Enter description:'
            }),
        }
