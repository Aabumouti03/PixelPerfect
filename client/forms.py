from django import forms
from .models import Program, Module, Category

class ProgramForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "category-checkbox"}),
        required=False
    )

    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.prefetch_related('categories'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['modules'].queryset = Module.objects.prefetch_related('categories')
