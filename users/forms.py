from django import forms

class SignUpForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=50)
    last_name = forms.CharField(label='Last Name')
    email = forms.EmailField(label='Email')
    gender = forms.CharField(label='Gender')
    age = forms.CharField(label='Age')
    sector = forms.CharField(label='Sector')
    last_time_worked = forms.CharField(label='Last time worked')
    ethnicity = forms.CharField(label='Ethnicity') #optional
    phone_number = forms.CharField(label='Phone Number') #optional
    password = forms.CharField(label='Password', widget=forms.PasswordInput())
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

