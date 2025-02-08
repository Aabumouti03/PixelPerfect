from django.db import models

class Program(models.Model):
    modules = models.ManyToManyField('Module', related_name= "programs")

class Module(models.Model):
    title = models.TextField(blank=False)
    #category = models.TextChoices


