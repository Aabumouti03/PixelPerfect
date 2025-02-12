from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from client.models import Program, Module, ExerciseQuestion

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)


class Admin(models.Model):
    user =  models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')

    def __str__(self):
        return f"Admin: {self.user.full_name()}"

class EndUser(models.Model):
    GENDER_OPTIONS = [
        ('female', 'Female'),
        ('male', 'Male'),
        ('other', 'Other'),
        ('N/A', 'Prefer not to say'),
    ]

    ETHNICITY_CHOICES = [
        ('asian', 'Asian'),
        ('black', 'Black or African Descent'),
        ('hispanic', 'Hispanic or Latino'),
        ('white', 'White or Caucasian'),
        ('middle_eastern', 'Middle Eastern or North African'),
        ('indigenous', 'Indigenous or Native'),
        ('south_asian', 'South Asian'),
        ('pacific_islander', 'Pacific Islander'),
        ('mixed', 'Mixed or Multiracial'),
        ('other', 'Other'),
        ('N/A', 'Prefer not to say'),
    ]

    TIME_DURATION_CHOICES = [
        ('1_month', 'In the last 1 month'),
        ('3_months', 'In the last 3 months'),
        ('6_months', 'In the last 6 months'),
        ('1_year', 'In the last 1 year'),
        ('2_years', 'In the last 2 years'),
        ('3_plus_years', 'More than 3 years ago'),
        ('never', 'Never worked before'),
    ]

    SECTOR_CHOICES = [
        ('it', 'Information Technology'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('finance', 'Finance'),
        ('engineering', 'Engineering'),
        ('retail', 'Retail & E-commerce'),
        ('hospitality', 'Hospitality & Tourism'),
        ('marketing', 'Marketing & Advertising'),
        ('government', 'Government & Public Service'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='User_profile')
    age = models.PositiveIntegerField(blank=False, null=True)  # Required
    gender = models.CharField(max_length=20, choices=GENDER_OPTIONS, blank=False, null = True)
    ethnicity = models.CharField(max_length=50, choices=ETHNICITY_CHOICES, blank=True, null=True)  # Optional
    program = models.OneToOneField(Program, on_delete=models.CASCADE, related_name="User_program")
    last_time_to_Work = models.CharField(max_length=20, choices=TIME_DURATION_CHOICES, blank=False, null= True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="User_modules")
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, blank=False, null = True)  # Required
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional


class UserResponse(models.Model):
    """Stores user answers for exercises."""
    user = models.ForeignKey('users.EndUser', on_delete=models.CASCADE) 
    question = models.ForeignKey('client.ExerciseQuestion', on_delete=models.CASCADE) 
    response_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Response by {self.user.user.username} for {self.question}"

