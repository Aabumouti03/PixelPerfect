from django import forms
from .models import User, EndUser
from django.core.validators import RegexValidator
from django.forms.widgets import Select, TextInput, EmailInput, PasswordInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


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


class LogInForm(AuthenticationForm):
    """Form for user log in."""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput()
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput()
    )


class EndUserProfileForm(forms.ModelForm):

    #  User fields related to User model
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

        # EndUser fields that need extra validation
    phone_number = forms.CharField(
        max_length=15, required=False,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")]
    )
    age = forms.IntegerField(min_value=18, max_value=100, required=True)  # Ensure realistic age

    class Meta:
        model = EndUser
        fields = ['phone_number', 'age', 'gender', 'ethnicity', 'last_time_to_Work', 'sector']


    def __init__(self, *args, **kwargs):
        """Initialize the form with existing data from the User model."""
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

            if hasattr(user, 'User_profile'):
                end_user = user.User_profile
                self.fields['phone_number'].initial = end_user.phone_number
                self.fields['age'].initial = end_user.age
                self.fields['gender'].initial = end_user.gender
                self.fields['ethnicity'].initial = end_user.ethnicity
                self.fields['last_time_to_Work'].initial = end_user.last_time_to_Work
                self.fields['sector'].initial = end_user.sector

    def clean_email(self):
        """Ensure email uniqueness, case insensitive."""
        email = self.cleaned_data.get('email', '').strip().lower()  
        user_id = self.instance.id if self.instance else None

        if User.objects.filter(email__iexact=email).exclude(id=user_id).exists():
            self.add_error('email', "This email is already in use.")  

        return email  

    def clean_username(self):
        """Ensure username uniqueness."""
        username = self.cleaned_data.get('username', '').strip()    
        user_id = self.instance.id if self.instance else None

        if User.objects.filter(username=username).exclude(id=user_id).exists():
            self.add_error('username', "This username is already taken.")  

        return username
    
    def save(self, commit=True):
        """Save both the User and EndUser fields."""
        end_user = super().save(commit=False)
        user = end_user.user 

        # Update User fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()  
            end_user.save()  

        return end_user  
