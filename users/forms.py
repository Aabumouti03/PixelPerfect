import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import User, EndUser
from django.utils.translation import gettext_lazy as _


class UserSignUpForm(UserCreationForm):
    """Form for creating a new user account with custom placeholders and password validation."""
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password: *'}),
        label=""
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter password: *'}),
        label=""
    )
 
    def clean_username(self):
        """Ensure username does not contain spaces and has at least 3 characters."""
        username = self.cleaned_data.get("username").lower()
        if " " in username:
            raise ValidationError("Username cannot contain spaces.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("A user with that username already exists.")
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
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username: *'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name: *'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name: *'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email: *'}),
        }

class EndUserProfileForm(forms.ModelForm):
    """Form for additional user profile information with age and phone number validation."""

    phone_number = forms.CharField(
    required=False,
    validators=[RegexValidator(
        r'^\+?\d{7,15}$',
        message="Enter a valid phone number (7-15 digits, optional '+')."
    )],
    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
)


    age = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age: *'}),
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
    
    def __init__(self, *args, **kwargs):
        """Convert choices to a list before modifying them."""
        super().__init__(*args, **kwargs)

        self.fields['gender'].choices = [("", "Select Gender: *")] + [choice for choice in self.fields['gender'].choices if choice[0] != '']
        self.fields['sector'].choices = [("", "Select Sector: *")] + [choice for choice in self.fields['sector'].choices if choice[0] != '']
        self.fields['ethnicity'].choices = [("", "Select Ethnicity:")] + [choice for choice in self.fields['ethnicity'].choices if choice[0] != '']
        self.fields['last_time_to_work'].choices = [("", "Select Time Since Last Work: *")] + [choice for choice in self.fields['last_time_to_work'].choices if choice[0] != '']

class LogInForm(AuthenticationForm):
    """Form for user log in."""
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )
    error_messages = {
         'invalid_login': _(
             "Incorrect username or password. Note that the password may be case-sensitive."
         ),
         'inactive': _("This account is inactive."),
     }

class UserProfileForm(forms.ModelForm):
    """This is for the user's profile section in the Profile Page."""
    #  User fields related to User model
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False, disabled=True)
    new_email = forms.EmailField(required=False)  # New email field


    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password', 'class': 'form-control'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password', 'class': 'form-control'}),
        label="Confirm Password"
    )

    # EndUser fields that need extra validation
    phone_number = forms.CharField(
        max_length=15, required=False,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number.")]
    )
    age = forms.IntegerField(min_value=18, max_value=100, required=True)  # Ensure realistic age

    class Meta:
        model = EndUser
        fields = ['phone_number', 'age', 'gender', 'ethnicity', 'last_time_to_work', 'sector']


    def __init__(self, *args, **kwargs):
        """Initialize the form with existing data from the User model."""
        user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['new_email'].initial = user.email

            if hasattr(user, 'User_profile'):
                end_user = user.User_profile
                self.fields['phone_number'].initial = end_user.phone_number
                self.fields['age'].initial = end_user.age
                self.fields['gender'].initial = end_user.gender
                self.fields['ethnicity'].initial = end_user.ethnicity
                self.fields['last_time_to_work'].initial = end_user.last_time_to_work
                self.fields['sector'].initial = end_user.sector

    def clean_first_name(self):
        """Ensure first name contains only letters."""
        first_name = self.cleaned_data.get("first_name", "").strip()

        if not first_name.isalpha():
            self.add_error("first_name", "First name should only contain letters.")

        return first_name

    def clean_last_name(self):
        """Ensure last name contains only letters."""
        last_name = self.cleaned_data.get("last_name", "").strip()

        if not last_name.isalpha():
            self.add_error("last_name", "Last name should only contain letters.")

        return last_name

    def clean_username(self):
        """Validate username based on the provided rules."""
        username = self.cleaned_data.get('username', '').strip()

        if len(username) < 3:
            self.add_error('username', "Username must be at least 3 characters long.")

        if " " in username:
            self.add_error('username', "Username should not contain spaces.")

        if not re.match(r'^\w+$', username):
            self.add_error('username', "Username can only contain letters, digits, and underscores.")

        # Ensure username is unique (excluding the current user)
        user_id = self.instance.user.id if hasattr(self.instance, 'user') else None
        if User.objects.exclude(id=user_id).filter(username=username).exists():
            self.add_error('username', "This username is already taken.")

        return username
    
    def clean_new_password(self):
        """Validate new password using Django's built-in rules + additional requirements."""
        new_password = self.cleaned_data.get("new_password")

        if new_password:
            # Apply Django's built-in password validation (checks length, common words, etc.)
            try:
                validate_password(new_password)
            except ValidationError as e:
                self.add_error('new_password', e)

            # Ensure password does not contain spaces
            if " " in new_password:
                self.add_error('new_password', "Password should not contain spaces.")

            # Ensure password contains at least one uppercase letter
            if not any(char.isupper() for char in new_password):
                self.add_error('new_password', "Password must contain at least one uppercase letter.")

            # Ensure password contains at least one lowercase letter
            if not any(char.islower() for char in new_password):
                self.add_error('new_password', "Password must contain at least one lowercase letter.")

            # Ensure password contains at least one number
            if not any(char.isdigit() for char in new_password):
                self.add_error('new_password', "Password must contain at least one number.")

        return new_password
    
    def clean_email(self):
        """Ensure email is unique, case-insensitive, and exclude the current user's email."""
        email = self.cleaned_data.get('email', '').strip().lower()  
        user_id = self.instance.user.id if hasattr(self.instance, 'user') else None  # Get User ID, not EndUser ID

        # Ensure email is unique (case insensitive), excluding the current user
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            self.add_error('email', "A user with this email already exists.")

        # Normalize email to lowercase before saving
        self.cleaned_data['email'] = email
        return email  
    

    def clean_new_email(self):
        """Ensure new email is unique, but allow pending verification."""
        new_email = self.cleaned_data.get('new_email', '').strip().lower()

        # Ensure instance exists and is an EndUser before accessing user
        if not isinstance(self.instance, EndUser) or not hasattr(self.instance, 'user') or not self.instance.user:
            self.add_error('new_email', "Internal error: EndUser is not linked to a User.")
            return new_email  # Prevent further validation issues

        user_id = self.instance.user.id

        if new_email and new_email != self.instance.user.email:
            # Exclude users who have the email in 'email' or 'new_email'
            if User.objects.exclude(id=user_id).filter(email=new_email).exists():
                self.add_error('new_email', "A user with this email already exists.")
            elif User.objects.exclude(id=user_id).filter(new_email=new_email).exists():
                self.add_error('new_email', "This email is already pending verification.")

        return new_email

    def clean(self):
        """Ensure new password and confirm password match."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match!")  

        return cleaned_data
    
    def save(self, commit=True):
        """Save both the User and EndUser fields."""
        end_user = super().save(commit=False)
        user = end_user.user 

        # Update User fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']

        # If user entered a new password, update it
        new_password = self.cleaned_data.get("new_password")
        if new_password:
            user.set_password(new_password)  

        if commit:
            user.save()  
            end_user.save()  

        return end_user  

class ExerciseAnswerForm(forms.Form):
    """
    Exercise Answer Form
    - The form takes an `exercise` object as an argument during initialization.
    - It dynamically creates form fields corresponding to each `ExerciseQuestion` linked to the exercise.
    - Each question field is labeled with its `question_text` and uses a `TextInput` widget.
    """
 
    def __init__(self, *args, **kwargs):
        exercise = kwargs.pop('exercise')  # Get exercise object
        super().__init__(*args, **kwargs)
        for question in exercise.questions.all():
            self.fields[f'answer_{question.id}'] = forms.CharField(
                label=question.question_text, 
                widget=forms.TextInput(attrs={'placeholder': 'Your answer here'})
            )
