from django.db import models
from django.conf import settings


EXERCISE_TYPES = [
    ('pdf', 'PDF Document'),
    ('fill_blank', 'Fill in the Blanks'),
    ('short_answer', 'Short Answer'),
    ('multiple_choice', 'Multiple Choice'),
]

QUESTION_TYPES = [
    ('fill_blank', 'Fill in the Blanks'),
    ('short_answer', 'Short Answer'),
    ('multiple_choice', 'Multiple Choice'),
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

    def __str__(self):
        return f"{self.title}"


class Exercise(models.Model):
    """An exercise within a section (Reusable)."""
    title = models.CharField(max_length=255)
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    questions = models.ManyToManyField('ExerciseQuestion', related_name="exercises", blank=True)  

    def __str__(self):
        return f"{self.title} ({self.exercise_type})"


class ExerciseQuestion(models.Model):
    """Each Exercise can have multiple Questions (0 to many)."""
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)  

    def __str__(self):
        return f"{self.question_text} ({self.question_type})"
