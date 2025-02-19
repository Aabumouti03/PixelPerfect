# Generated by Django 5.1.6 on 2025-02-18 16:13

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resource_type', models.CharField(choices=[('book', 'Book'), ('podcast', 'Podcast'), ('survey', 'Survey'), ('pdf', 'PDF Document'), ('link', 'External Link')], max_length=10)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='resources/')),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ExerciseQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('has_blank', models.BooleanField(default=False)),
                ('text_before_blank', models.TextField(blank=True, null=True)),
                ('text_after_blank', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('MULTIPLE_CHOICE', 'Multiple Choice'), ('RATING', 'Rating Scale')], max_length=20)),
                ('is_required', models.BooleanField(default=True)),
                ('min_rating', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('max_rating', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(10)])),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('exercise_type', models.CharField(choices=[('fill_blank', 'Fill in the Blanks'), ('short_answer', 'Short Answer'), ('multiple_choice', 'Multiple Choice')], max_length=20)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('questions', models.ManyToManyField(blank=True, related_name='exercises', to='client.exercisequestion')),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='client.question')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='client.questionnaire'),
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('diagram', models.ImageField(blank=True, null=True, upload_to='diagrams/')),
                ('text_position_from_diagram', models.CharField(choices=[('above', 'Above the Diagram'), ('below', 'Below the Diagram'), ('left', 'Left of the Diagram'), ('right', 'Right of the Diagram')], default='below', max_length=10)),
                ('exercises', models.ManyToManyField(related_name='sections', to='client.exercise')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('additional_resources', models.ManyToManyField(blank=True, related_name='sections', to='client.additionalresource')),
                ('categories', models.ManyToManyField(related_name='modules', to='client.category')),
                ('sections', models.ManyToManyField(related_name='modules', to='client.section')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_programs', to='client.module')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_modules', to='client.program')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('program', 'order')},
            },
        ),
    ]
