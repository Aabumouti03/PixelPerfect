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

    def clean_title(self):
        """Ensure program title is unique, case-insensitively."""
        title = self.cleaned_data.get("title")
        if Program.objects.filter(title__iexact=title).exists():
            raise forms.ValidationError("A program with this title already exists.")
        return title


    def clean_description(self):
        """Ensure the description is provided."""
        description = self.cleaned_data.get("description")
        if not description:
            raise forms.ValidationError("Description is required.")
        return description
    


class CategoryForm(forms.ModelForm):
    modules = forms.ModelMultipleChoiceField(
        queryset=Module.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "module-checkbox"}),
        required=False,
        label="Select Modules"
    )
    programs = forms.ModelMultipleChoiceField(
        queryset=Program.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "program-checkbox"}),
        required=False,
        label="Select Programs"
    )

    class Meta:
        model = Category
        fields = ['name', 'modules', 'programs']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control rounded-pill border-2',
                'placeholder': 'Enter category name:'
            }),
        }