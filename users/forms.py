from django import forms
from django.forms.widgets import Select, TextInput, EmailInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, EndUser


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserSignUpForm(UserCreationForm):
    """Form for creating a new user account with custom placeholders."""
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter password'}),
        label=""
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

class EndUserProfileForm(forms.ModelForm):
    """Form for additional user profile information."""
    
    class Meta:
        model = EndUser
        fields = ['age', 'gender', 'sector', 'ethnicity', 'last_time_to_work', 'phone_number']
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.GENDER_OPTIONS),
            'sector': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.SECTOR_CHOICES),
            'ethnicity': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.ETHNICITY_CHOICES),
            'last_time_to_work': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.TIME_DURATION_CHOICES),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

class LogInForm(AuthenticationForm):
    """Form for user log in."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )

class ExerciseAnswerForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        exercise = kwargs.pop('exercise')  # Get exercise object
        super().__init__(*args, **kwargs)
        for question in exercise.questions.all():
            self.fields[f'answer_{question.id}'] = forms.CharField(
                label=question.question_text, 
                widget=forms.TextInput(attrs={'placeholder': 'Your answer here'})
            )
