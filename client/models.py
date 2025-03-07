from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

# Choices for Exercise Types
EXERCISE_TYPES = [
    ('fill_blank', 'Fill in the Blanks'),
    ('short_answer', 'Short Answer'),
    ('multiple_choice', 'Multiple Choice'),
]

# Choices for Question Placement Relative to Diagram
QUESTION_POSITIONS = [
    ('above', 'Above the Diagram'),
    ('below', 'Below the Diagram'),
    ('left', 'Left of the Diagram'),
    ('right', 'Right of the Diagram'),
]

STATUS_CHOICES = [
        ('not_started','Not Started'),
        ('in_progress', 'In_Progress'),
        ('completed', 'Completed')
]


BACKGROUND_IMAGE_CHOICES = [
    ('pattern1', 'url("data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'%3E%3Ccircle cx=\'3\' cy=\'3\' r=\'3\'/%3E%3Ccircle cx=\'13\' cy=\'13\' r=\'3\'/%3E%3C/g%3E%3C/svg%3E")'),
    ('pattern2', 'url("data:image/svg+xml,%3Csvg width=\'84\' height=\'48\' viewBox=\'0 0 84 48\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M0 0h12v6H0V0zm28 8h12v6H28V8zm14-8h12v6H42V0zm14 0h12v6H56V0zm0 8h12v6H56V8zM42 8h12v6H42V8zm0 16h12v6H42v-6zm14-8h12v6H56v-6zm14 0h12v6H70v-6zm0-16h12v6H70V0zM28 32h12v6H28v-6zM14 16h12v6H14v-6zM0 24h12v6H0v-6zm0 8h12v6H0v-6zm14 0h12v6H14v-6zm14 8h12v6H28v-6zm-14 0h12v6H14v-6zm28 0h12v6H42v-6zm14-8h12v6H56v-6zm0-8h12v6H56v-6zm14 8h12v6H70v-6zm0 8h12v6H70v-6zM14 24h12v6H14v-6zm14-8h12v6H28v-6zM14 8h12v6H14V8zM0 8h12v6H0V8z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'),
    ('pattern3', 'url("data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M20 20.5V18H0v-2h20v-2H0v-2h20v-2H0V8h20V6H0V4h20V2H0V0h22v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2v2H20v-1.5zM0 20h2v20H0V20zm4 0h2v20H4V20zm4 0h2v20H8V20zm4 0h2v20h-2V20zm4 0h2v20h-2V20zm4 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'),
    ('pattern4', 'url("data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M0 0h20L0 20z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'),
    ('pattern5', 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'112\' height=\'92\' viewBox=\'0 0 112 92\'%3E%3Cg fill=\'%230148fd\' fill-opacity=\'0.18\'%3E%3Cpath fill-rule=\'evenodd\' d=\'M72 10H40L16 20H0v8h16l24-14h32l24 14h16v-8H96L72 10zm0-8H40L16 4H0v8h16l24-6h32l24 6h16V4H96L72 2zm0 84H40l-24-6H0v8h16l24 2h32l24-2h16v-8H96l-24 6zm0-8H40L16 64H0v8h16l24 10h32l24-10h16v-8H96L72 78zm0-12H40L16 56H0v4h16l24 14h32l24-14h16v-4H96L72 66zm0-16H40l-24-2H0v4h16l24 6h32l24-6h16v-4H96l-24 2zm0-16H40l-24 6H0v4h16l24-2h32l24 2h16v-4H96l-24-6zm0-16H40L16 32H0v4h16l24-10h32l24 10h16v-4H96L72 18z\'/%3E%3C/g%3E%3C/svg%3E")'),
]

class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    

class Program(models.Model):
    """A program that consists of multiple modules (Reusable)."""
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name="programs")
    description = models.TextField(blank=True, null=True)
    modules = models.ManyToManyField('Module',through='ProgramModule', related_name="programs")  

    def __str__(self):
        return self.title

class ProgramModule(models.Model):
    """Intermediary table for ordering modules within a program."""
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="program_modules")  
    module = models.ForeignKey('Module', on_delete=models.CASCADE, related_name="module_programs")  
    order = models.PositiveIntegerField()  

    class Meta:
        unique_together = ('program', 'order')  #Prevents duplicate order numbers within a program
        ordering = ['order']  # Always retrieve modules in correct sequence

    def __str__(self):
        return f"{self.program.title} - {self.module.title} (Order: {self.order})"

class BackgroundStyle(models.Model):
    """Model to store background color and image URL."""
    background_color = models.CharField(max_length=7, default='#73c4fd')  # Hex color code
    background_image = models.CharField(
        max_length=20,
        choices=BACKGROUND_IMAGE_CHOICES,
        default='pattern1', 
    )

    def get_background_image_url(self):
        """Returns the full background image URL based on the selected choice."""
        for key, value in BACKGROUND_IMAGE_CHOICES:
            if key == self.background_image:
                return value
        return None

    def __str__(self):
        return f"Background Style: {self.background_color} - {self.background_image}"

class Module(models.Model):
    """A module that contains multiple sections (Reusable)."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name="modules")
    sections = models.ManyToManyField('Section', related_name="modules")  
    additional_resources = models.ManyToManyField('AdditionalResource', blank=True, related_name="sections")
    background_style = models.ForeignKey(BackgroundStyle, on_delete=models.SET_NULL, null=True, blank=True)

    def average_rating(self):
        avg_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0


    def __str__(self):
        return self.title

<<<<<<< HEAD

class ModuleRating(models.Model):
    """Tracks user ratings for a module."""
    module = models.ForeignKey("client.Module", related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey("users.EndUser", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('module', 'user')  # Ensures a user can rate a module only once.

    def __str__(self):
        return f"{self.user.user.username} rated {self.module.title} - {self.rating}/5"


=======
>>>>>>> profilePage
class Section(models.Model):
    """A section that can be used across multiple modules."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exercises = models.ManyToManyField('Exercise', related_name="sections")  
    diagram = models.ImageField(upload_to='diagrams/', blank=True, null=True)  
    text_position_from_diagram = models.CharField(
        max_length=10, choices=QUESTION_POSITIONS, default='below' 
    )
    
    def __str__(self):
        return f"{self.title} (Diagram: {'Yes' if self.diagram else 'No'})"


class AdditionalResource(models.Model):
    """A model to store additional resources such as books, podcasts, and surveys."""
    RESOURCE_TYPES = [
        ('book', 'Book'),
        ('podcast', 'Podcast'),
        ('survey', 'Survey'),
        ('pdf', 'PDF Document'),
        ('link', 'External Link'),
    ]
    
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='resources/', blank=True, null=True)  # For PDFs
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    url = models.URLField(blank=True, null=True)  # For external links
    
    def __str__(self):
        return f"{self.title} ({self.resource_type})"


class Exercise(models.Model):
    """An exercise within a section (Reusable)."""
    title = models.CharField(max_length=255)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    questions = models.ManyToManyField('ExerciseQuestion', related_name="exercises", blank=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started') 

    def save(self, *args, **kwargs):
        """Auto-set exercise_type based on questions if not set."""
        if not self.exercise_type and self.questions.exists():
            first_question = self.questions.first()
            if first_question.has_blank:
                self.exercise_type = 'fill_blank'
            else:
                self.exercise_type = 'short_answer'  # Default if no blanks
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.exercise_type})"


class ExerciseQuestion(models.Model):
    """Each Exercise can have multiple Questions (0 to many)."""
    question_text = models.TextField()
    has_blank = models.BooleanField(default=False)  
    text_before_blank = models.TextField(blank=True, null=True)  
    text_after_blank = models.TextField(blank=True, null=True)  

    def clean(self):
        """Ensure at least one of 'text_before_blank' or 'text_after_blank' is filled when 'has_blank' is True."""
        if self.has_blank:
            if not self.text_before_blank and not self.text_after_blank:
                raise ValidationError(
                    "At least one of 'text_before_blank' or 'text_after_blank' must be provided when 'has_blank' is True."
                )

    def __str__(self):
        if self.has_blank:
            return f"{self.text_before_blank} ____ {self.text_after_blank}"
        return f"{self.question_text}"

# Questionnaire

class Questionnaire (models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Question (models.Model):
    QUESTION_TYPES = [
        ('AGREEMENT', 'Agreement Scale'),
        ('RATING', 'Rating Scale'),
    ]
    SENTIMENT_CHOICES = [
        (1, 'Positive'),
        (0, 'Neutral'),
        (-1, 'Negative'),
    ]
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField(blank=False)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)  # 🆕 Added for categorization
    sentiment = models.IntegerField(choices=SENTIMENT_CHOICES, default=1)  # +1 for positive, -1 for negative

    # For rating questions
    #FIXED RATING SCALE (1 to 5)
    FIXED_MIN_RATING = 1
    FIXED_MAX_RATING = 5

    def __str__(self):
        return f"{self.questionnaire.title} - {self.question_text[:30]}"
    


