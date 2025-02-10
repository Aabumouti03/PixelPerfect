from django import forms
from django.core.exceptions import ValidationError
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()   # Convert to lowercase
        user_id = self.instance.id if self.instance else None

        # Case-insensitive uniqueness check, excluding the current user
        if User.objects.filter(email__iexact=email).exclude(id=user_id).exists():
            self.add_error('email', "This email is already in use.")  

        return email  

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()    # Do NOT convert to lowercase
        user_id = self.instance.id if self.instance else None

        # Case-sensitive uniqueness check, excluding the current user
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            self.add_error('username', "This username is already taken.")  

        return username  
    



