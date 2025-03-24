from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from client.models import Program, Module, Questionnaire, Question, Exercise, VideoResource, AdditionalResource
from django.core.exceptions import ValidationError 
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.exceptions import ValidationError


from django.core.cache import cache
import random
import datetime

#Choices used in more than one model
STATUS_CHOICES = [
        ('not_started','Not Started'),
        ('in_progress', 'In_Progress'),
        ('completed', 'Completed')
]

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^\w{3,}$',
            message='Username must consist at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    # Fields for email change verification
    new_email = models.EmailField(unique=True, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

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
    
    def save(self, *args, **kwargs):
         if self.username:
             self.username = self.username.lower()
         super().save(*args, **kwargs)


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
    last_time_to_work = models.CharField(max_length=20, choices=TIME_DURATION_CHOICES, blank=False, null= True)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, blank=False, null = True)  # Required
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional

    def __str__(self):
        return f"User: {self.user.full_name()}"


class UserProgramEnrollment(models.Model):
    """Tracks when a user enrolls in a program."""
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='program_enrollments')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} enrolled in {self.program.title}"
    

class UserModuleEnrollment(models.Model):
    """Tracks when a user starts a standalone module."""
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='module_enrollments')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='enrolled_users')
    enrolled_on = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"{self.user.user.username} started {self.module.title}"


class UserProgramProgress (models.Model):

    user = models.ForeignKey(EndUser, on_delete=models.CASCADE,related_name='program_progress')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='user_progress')
    completion_percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'program')
    def __str__(self):
        return f"{self.user.full_name()} - {self.program.title} ({self.status})"
    
class UserModuleProgress(models.Model):

    user = models.ForeignKey(EndUser, on_delete=models.CASCADE,related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE,related_name='user_progress')
    completion_percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'module') 
    def __str__(self):
        return f"{self.user.full_name()} - {self.module.title} ({self.status})"

class UserResourceProgress(models.Model):
    """Tracks user progress for each additional resource."""
    user = models.ForeignKey("users.EndUser", on_delete=models.CASCADE)
    resource = models.ForeignKey("client.AdditionalResource", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    class Meta:
        unique_together = ('user', 'resource')

    def __str__(self):
        return f"{self.user.user.username} - {self.resource.title}: {self.status}"


class UserExerciseProgress(models.Model):
    """Tracks user progress for each exercise."""
    user = models.ForeignKey("users.EndUser", on_delete=models.CASCADE)
    exercise = models.ForeignKey("client.Exercise", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    class Meta:
        unique_together = ('user', 'exercise')

    def __str__(self):
        return f"{self.user.user.username} - {self.exercise.title}: {self.status}"


class UserVideoProgress(models.Model):
    """Tracks user progress for each video resource."""
    user = models.ForeignKey("users.EndUser", on_delete=models.CASCADE)
    video = models.ForeignKey("client.VideoResource", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.user.username} - {self.video.title}: {self.status}"



class UserResponse(models.Model):
    """Stores user answers for exercises."""
    user = models.ForeignKey('users.EndUser', on_delete=models.CASCADE) 
    question = models.ForeignKey('client.ExerciseQuestion', on_delete=models.CASCADE) 
    response_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Response by {self.user.user.username} for {self.question}"


# Questionnaire-related models
class Questionnaire_UserResponse(models.Model):
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
        

class QuestionResponse(models.Model):
    user_response = models.ForeignKey(Questionnaire_UserResponse, related_name='question_responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    rating_value = models.IntegerField(
    null=True, 
    blank=True, 
    validators=[MinValueValidator(-2), MaxValueValidator(2)]
    )
    
    def clean(self):
        if self.question.question_type == 'RATING' and self.rating_value is None:
            raise ValidationError('Rating scale questions require a rating value')

        if self.question.question_type == 'AGREEMENT' and self.rating_value is None:
            raise ValidationError('Agreement scale questions require a selection')


class StickyNote(models.Model):
    user = models.ForeignKey(EndUser, on_delete=models.CASCADE, related_name='sticky_notes')
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"StickyNote by {self.user.user.username}"


class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=now)

    connected_with_family = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], blank=True, null=True)
    expressed_gratitude = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], blank=True, null=True)
    caffeine = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], blank=True, null=True)
    hydration = models.PositiveIntegerField(blank=True, null=True)
    goal_progress = models.CharField(max_length=10, choices=[("low", "Low"), ("moderate", "Moderate"), ("high", "High")], blank=True, null=True)
    outdoors = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], blank=True, null=True)
    sunset = models.CharField(max_length=3, choices=[("yes", "Yes"), ("no", "No")], blank=True, null=True)
    stress = models.CharField(max_length=10, choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")], blank=True, null=True)
    sleep_hours = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
class Quote(models.Model):
    text = models.TextField()

    def __str__(self):
        return f'"{self.text}"'

    @staticmethod
    def get_quote_of_the_day():
        """Returns the same quote for the entire day and updates it once per day."""
        today = now().date()

        daily_quote, created = DailyQuote.objects.get_or_create(date=today)

        if not created and daily_quote.quote:
            return daily_quote.quote.text

        count = Quote.objects.count()
        if count == 0:
            return "No quote available today."

        new_quote = Quote.objects.order_by("?").first()
        daily_quote.quote = new_quote
        daily_quote.save()

        return new_quote.text
    
class DailyQuote(models.Model):
    date = models.DateField(unique=True)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Daily Quote for {self.date}: {self.quote.text if self.quote else 'None'}"