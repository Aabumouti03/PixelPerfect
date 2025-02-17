from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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

class Program(models.Model):
    """A program that consists of multiple modules (Reusable)."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    modules = models.ManyToManyField('Module', related_name="programs")  

    def __str__(self):
        return self.title


class Module(models.Model):
    """A module that contains multiple sections (Reusable)."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sections = models.ManyToManyField('Section', related_name="modules")  

    def __str__(self):
        return self.title


class Section(models.Model):
    """A section that can be used across multiple modules."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    exercises = models.ManyToManyField('Exercise', related_name="sections")  
    diagram = models.ImageField(upload_to='diagrams/', blank=True, null=True)  
    text_position_from_diagram = models.CharField(
        max_length=10, choices=QUESTION_POSITIONS, default='below' 
    )
    
    # ✅ Additional Resources for Sections
    additional_resources = models.ManyToManyField('AdditionalResource', blank=True, related_name="sections")

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
    url = models.URLField(blank=True, null=True)  # For external links
    
    def __str__(self):
        return f"{self.title} ({self.resource_type})"


class Exercise(models.Model):
    """An exercise within a section (Reusable)."""
    title = models.CharField(max_length=255)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    questions = models.ManyToManyField('ExerciseQuestion', related_name="exercises", blank=True)  

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
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('RATING', 'Rating Scale'),
    ]
    questionnaire = models.ForeignKey(Questionnaire, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField(blank=False)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=True)

    # For rating questions
    min_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    max_rating = models.IntegerField(null=True, blank=True, validators=[MaxValueValidator(10)])

    def __str__(self):
        return f"{self.questionnaire.title} - {self.question_text[:30]}"
    
class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.text
    

