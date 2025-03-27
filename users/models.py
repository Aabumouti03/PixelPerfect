from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from libgravatar import Gravatar
from client.models import Program, Module, Questionnaire, Question
from django.core.exceptions import ValidationError 
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
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
        return f"{self.user.user.full_name()} - {self.program.title} ({self.status})"
    
class UserModuleProgress(models.Model):

    user = models.ForeignKey(EndUser, on_delete=models.CASCADE,related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE,related_name='user_progress')
    completion_percentage = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'module') 
    def __str__(self):
        return f"{self.user.user.full_name()} - {self.module.title} ({self.status})"

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
    question = models.ForeignKey('client.ExerciseQuestion', on_delete=models.CASCADE, related_name='responses') 
    response_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)  

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
        
        Quote.ensure_default_quotes_exist()

        new_quote = Quote.objects.order_by("?").first()

        if new_quote is None:  
            return "No quote available today."
        
        daily_quote.quote = new_quote
        daily_quote.save()

        return new_quote.text
    
    @staticmethod
    def ensure_default_quotes_exist():
        """Populate default quotes if they are missing."""
        quotes = [
            "Success is not the key to happiness. Happiness is the key to success. — Albert Schweitzer",
            "Your limitation—it’s only your imagination.",
            "Do what you can, with what you have, where you are. — Theodore Roosevelt",
            "Dream big and dare to fail. — Norman Vaughan",
            "Opportunities don't happen. You create them. — Chris Grosser",
            "Don't let yesterday take up too much of today. — Will Rogers",
            "The only way to do great work is to love what you do. — Steve Jobs",
            "Act as if what you do makes a difference. It does. — William James",
            "Believe you can and you're halfway there. — Theodore Roosevelt",
            "Every day may not be good, but there's something good in every day.",
            "Keep your face always toward the sunshine—and shadows will fall behind you. — Walt Whitman",
            "You are never too old to set another goal or to dream a new dream. — C.S. Lewis",
            "Difficult roads often lead to beautiful destinations.",
            "You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
            "Happiness is not something ready-made. It comes from your own actions. — Dalai Lama",
            "Work hard in silence, let your success be your noise. — Frank Ocean",
            "Failure is simply the opportunity to begin again, this time more intelligently. — Henry Ford",
            "Live as if you were to die tomorrow. Learn as if you were to live forever. — Mahatma Gandhi",
            "Start where you are. Use what you have. Do what you can. — Arthur Ashe",
            "If you want to lift yourself up, lift up someone else. — Booker T. Washington",
            "No one is perfect—that’s why pencils have erasers. — Wolfgang Riebe",
            "Success is getting what you want. Happiness is wanting what you get. — Dale Carnegie",
            "Happiness depends upon ourselves. — Aristotle",
            "You are capable of amazing things.",
            "Do what makes your soul shine.",
            "What lies behind us and what lies before us are tiny matters compared to what lies within us. — Ralph Waldo Emerson",
            "Don't watch the clock; do what it does. Keep going. — Sam Levenson",
            "Small steps in the right direction can turn out to be the biggest step of your life.",
            "Happiness is a direction, not a place. — Sydney J. Harris",
            "If opportunity doesn’t knock, build a door. — Milton Berle",
            "The best way to predict the future is to create it. — Peter Drucker",
            "Be kind whenever possible. It is always possible. — Dalai Lama",
            "You were born to be real, not to be perfect.",
            "Be yourself; everyone else is already taken. — Oscar Wilde",
            "Stay close to anything that makes you glad you are alive. — Hafiz",
            "Enjoy the little things, for one day you may look back and realize they were the big things. — Robert Brault",
            "Your vibe attracts your tribe.",
            "Be strong. You never know who you are inspiring.",
            "Turn your wounds into wisdom. — Oprah Winfrey",
            "Be a voice, not an echo.",
            "With the new day comes new strength and new thoughts. — Eleanor Roosevelt",
            "You are enough just as you are.",
            "A champion is defined not by their wins but by how they can recover when they fall. — Serena Williams",
            "Your life only gets better when you get better.",
            "Happiness is not by chance, but by choice. — Jim Rohn",
            "It always seems impossible until it's done. — Nelson Mandela",
            "Do more of what makes you happy.",
            "Life isn’t about waiting for the storm to pass, it’s about learning to dance in the rain. — Vivian Greene",
            "Success is falling nine times and getting up ten. — Jon Bon Jovi",
            "You didn’t come this far to only come this far.",
            "Some people want it to happen, some wish it would happen, others make it happen. — Michael Jordan",
            "Let your dreams be bigger than your fears.",
            "Doubt kills more dreams than failure ever will. — Suzy Kassem",
            "Every day is a second chance.",
            "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle.",
            "Never bend your head. Always hold it high. Look the world straight in the eye. — Helen Keller",
            "Be the reason someone smiles today.",
            "Rise above the storm and you will find the sunshine. — Mario Fernandez",
            "Take the risk or lose the chance.",
            "Happiness is letting go of what you think your life is supposed to look like.",
            "A goal without a plan is just a wish. — Antoine de Saint-Exupéry",
            "Keep going. Everything you need will come to you at the perfect time.",
            "You are stronger than you think.",
            "The only thing you can control is your own effort.",
            "Wake up with determination, go to bed with satisfaction.",
            "Make today so awesome that yesterday gets jealous.",
            "Trust the timing of your life.",
            "Everything you can imagine is real. — Pablo Picasso",
            "What consumes your mind, controls your life.",
            "Stay positive, work hard, make it happen.",
            "Hardships often prepare ordinary people for an extraordinary destiny. — C.S. Lewis",
            "Kindness is a language which the deaf can hear and the blind can see. — Mark Twain",
            "The more you give away, the more happy you become. — Dalai Lama",
            "Light tomorrow with today. — Elizabeth Barrett Browning",
            "Sometimes when you're in a dark place you think you've been buried, but you've actually been planted. — Christine Caine",
            "Do what is right, not what is easy.",
            "Nothing is impossible, the word itself says 'I'm possible!' — Audrey Hepburn",
            "Success usually comes to those who are too busy to be looking for it. — Henry David Thoreau",
            "It is during our darkest moments that we must focus to see the light. — Aristotle",
            "Act as if what you do makes a difference. It does. — William James",
            "Opportunities don’t happen, you create them. — Chris Grosser",
            "The best way to get started is to quit talking and begin doing. — Walt Disney",
            "The secret of getting ahead is getting started. — Mark Twain",
            "The only limit to our realization of tomorrow is our doubts of today. — Franklin D. Roosevelt",
            "Whatever the mind can conceive and believe, it can achieve. — Napoleon Hill"
        ]


        if not Quote.objects.exists():
            for quote_text in quotes:
                Quote.objects.create(text=quote_text)
    
class DailyQuote(models.Model):
    date = models.DateField(unique=True)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Daily Quote for {self.date}: {self.quote.text if self.quote else 'None'}"