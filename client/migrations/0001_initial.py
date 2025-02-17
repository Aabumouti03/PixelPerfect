# Generated by Django 5.1.2 on 2025-02-15 18:10

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
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
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
            name='Program',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('modules', models.ManyToManyField(related_name='programs', to='client.module')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('diagram', models.ImageField(blank=True, null=True, upload_to='diagrams/')),
                ('text_position_from_diagram', models.CharField(choices=[('above', 'Above the Diagram'), ('below', 'Below the Diagram'), ('left', 'Left of the Diagram'), ('right', 'Right of the Diagram')], default='below', max_length=10)),
                ('additional_resources', models.ManyToManyField(blank=True, related_name='sections', to='client.additionalresource')),
                ('exercises', models.ManyToManyField(related_name='sections', to='client.exercise')),
            ],
        ),
        migrations.AddField(
            model_name='module',
            name='sections',
            field=models.ManyToManyField(related_name='modules', to='client.section'),
        ),
    ]
