from django import forms
from django.forms.widgets import Select, TextInput, EmailInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm
from .models import User, EndUser


class UserSignUpForm(UserCreationForm):
    """Form for creating a new user account."""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class EndUserProfileForm(forms.ModelForm):
    """Form for additional user profile information."""
    
    class Meta:
        model = EndUser
        fields = ['age', 'gender', 'sector', 'ethnicity', 'last_time_to_work', 'phone_number']