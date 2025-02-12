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

