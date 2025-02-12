# Generated by Django 5.1.6 on 2025-02-12 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0003_exercise_question_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exercise',
            name='question',
        ),
        migrations.RemoveField(
            model_name='exercisequestion',
            name='exercise',
        ),
        migrations.AddField(
            model_name='exercise',
            name='questions',
            field=models.ManyToManyField(blank=True, related_name='exercises', to='client.exercisequestion'),
        ),
    ]
