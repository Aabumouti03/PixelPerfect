from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, EndUser
from django.contrib.auth.password_validation import validate_password

class UserSignUpForm(UserCreationForm):
    """Form for creating a new user account with custom placeholders and password validation."""
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter password'}),
        label=""
    )

    def clean_username(self):
        """Ensure username does not contain spaces and has at least 3 characters."""
        username = self.cleaned_data.get("username")
        if " " in username:
            raise ValidationError("Username cannot contain spaces.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        return username

    def clean_password1(self):
        """Validate password strength, including checking for common passwords and no spaces."""
        password = self.cleaned_data.get("password1")
        if " " in password:
            raise ValidationError("Password cannot contain spaces.")
        if not any(char.isupper() for char in password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("Password must contain at least one number.")
        validate_password(password)
        return password


    def clean_password2(self):
        """Ensure password confirmation matches."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords must match.")
        return password2

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_first_name(self):
        """Ensure first name contains only letters."""
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise ValidationError("First name must contain only letters.")
        return first_name

    def clean_last_name(self):
        """Ensure last name contains only letters."""
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise ValidationError("Last name must contain only letters.")
        return last_name

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
    """Form for additional user profile information with age and phone number validation."""

    phone_number = forms.CharField(
        validators=[RegexValidator(r'^\+?[1-9]\d{6,14}$', message="Enter a valid phone number (7-15 digits, optional '+').")],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'}),
        required=True
    )

    def clean_age(self):
        """Validate that age is within a reasonable range."""
        age = self.cleaned_data.get("age")
        if age and (age < 18 or age > 100):
            raise ValidationError("Enter a valid age between 18 and 100.")
        return age

    class Meta:
        model = EndUser
        fields = ['age', 'gender', 'sector', 'ethnicity', 'last_time_to_work', 'phone_number']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.GENDER_OPTIONS),
            'sector': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.SECTOR_CHOICES),
            'ethnicity': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.ETHNICITY_CHOICES),
            'last_time_to_work': forms.Select(attrs={'class': 'form-control'}, choices=EndUser.TIME_DURATION_CHOICES),
        }

class LogInForm(AuthenticationForm):
    """Form for user log in."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )
