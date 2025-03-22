from django import forms
from .models import Program, Module, Category, ProgramModule, VideoResource

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
    
    new_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control rounded-pill border-2",
            "placeholder": "Enter a new category (optional)"
        }),
    )

    class Meta:
        model = Program
        fields = ['title', 'description', 'modules', 'module_order', 'categories', 'new_category']
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

    def clean_new_category(self):
        """Ensure the new category does not already exist and reuse if possible."""
        new_category = self.cleaned_data.get("new_category", "").strip()
        
        if new_category:
            existing_category = Category.objects.filter(name__iexact=new_category).first()
            if existing_category:
                return existing_category.name
        
        return new_category

    
    def clean_description(self):
        """Ensure description is not empty or just whitespace."""
        description = self.cleaned_data.get("description", "").strip()
        if not description:
            raise forms.ValidationError("Description cannot be empty.")
        return description


    def save(self, commit=True):
        """Override save to ensure module ordering and categories are handled correctly."""
        program = super().save(commit=False)

        if commit:
            program.save()

            new_category_name = self.cleaned_data.get("new_category", "").strip()
            if new_category_name:
                new_category, created = Category.objects.get_or_create(name=new_category_name)
                program.categories.add(new_category)

            selected_categories = self.cleaned_data.get("categories", [])
            program.categories.add(*selected_categories)

            ProgramModule.objects.filter(program=program).delete()

            selected_modules = self.cleaned_data.get("modules", [])

            module_order_data = self.cleaned_data.get("module_order", "")

            if module_order_data:
                ordered_module_ids = [int(id) for id in module_order_data.split(",") if id.isdigit()]
            else:
                ordered_module_ids = [module.id for module in selected_modules]

            for order, module_id in enumerate(ordered_module_ids, start=1):
                module = Module.objects.get(id=module_id)
                if module in selected_modules:
                    ProgramModule.objects.create(program=program, module=module, order=order)

        return program

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

#fir uploading video content
class VideoResourceForm(forms.ModelForm):
    class Meta:
        model = VideoResource
        fields = ['title', 'description', 'youtube_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter video description'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Paste YouTube video URL'}),
        }
        
class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter module title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter module description'
            }),
        }

    def clean_title(self):
        """Ensure module title is unique, case-insensitively."""
        title = self.cleaned_data.get('title')
        if Module.objects.filter(title__iexact=title).exists():
            raise forms.ValidationError('A module with this title already exists.')
        return title