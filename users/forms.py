from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import EndUser
from django.contrib.auth.forms import AuthenticationForm

class SignUpForm(UserCreationForm):
    password_confirmation = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput()
    )

    
    def clean(self):
        """Validate password and password confirmation match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data

# You can optionally customize the AuthenticationForm if needed
class LogInForm(AuthenticationForm):
    # If you need to add custom widgets or fields, you can modify the form here
    pass