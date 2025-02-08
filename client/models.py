from django.db import models
from django.core.exceptions import ValidationError

class Program(models.Model):
    modules = models.ManyToManyField('Module', related_name= "programs")

class Module(models.Model):
    title = models.TextField(blank=False)
    #category = models.TextChoices
    #videos 
    #infosheets
    #excercises
    #tasks

class Questionnaire(models.Model):
    title = models.TextField(blank=False)
    questions = models.ManyToManyField('Question', related_name='questionnaires')

class Question(models.Model):
    """Model representing a question in a questionnaire."""
    QUESTION_TYPES = [
        ('boolean', 'This or That'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating Scale'),
    ]

    question_text = models.TextField()
    type = models.TextField(choices=QUESTION_TYPES)

    # Add a related_name to avoid reverse accessor conflicts
    option_set = models.OneToOneField(
        'QuestionOption', on_delete=models.SET_NULL, null=True, blank=True, related_name='question_option'
    )

    def __str__(self):
        return self.question_text

    def clean(self):
        """Ensure only multiple-choice questions have options."""
        if self.type != 'multiple_choice' and self.option_set:
            raise ValidationError('Options can only be linked to multiple-choice questions.')


class QuestionOption(models.Model):
    """Container for options related to a question."""
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='options')
    QuestionOptions = models.ForeignKey(
        'Option', on_delete=models.CASCADE, related_name='question_options', null=True, blank=True
    )

    def __str__(self):
        return f"Options for: {self.question.question_text}"



class Option(models.Model):
    """Individual options related to a QuestionOption."""
    question_option = models.ForeignKey(
        'QuestionOption', on_delete=models.CASCADE, related_name='options', null=True, blank=True
    )
    option_text = models.TextField(blank=False)

    def __str__(self):
        return self.option_text

