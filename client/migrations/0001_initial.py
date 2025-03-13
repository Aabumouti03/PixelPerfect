# Generated by Django 5.1.6 on 2025-03-13 21:14

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
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BackgroundStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('background_color', models.CharField(default='#73c4fd', max_length=7)),
                ('background_image', models.CharField(choices=[('pattern1', 'url("data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'%3E%3Ccircle cx=\'3\' cy=\'3\' r=\'3\'/%3E%3Ccircle cx=\'13\' cy=\'13\' r=\'3\'/%3E%3C/g%3E%3C/svg%3E")'), ('pattern2', 'url("data:image/svg+xml,%3Csvg width=\'84\' height=\'48\' viewBox=\'0 0 84 48\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M0 0h12v6H0V0zm28 8h12v6H28V8zm14-8h12v6H42V0zm14 0h12v6H56V0zm0 8h12v6H56V8zM42 8h12v6H42V8zm0 16h12v6H42v-6zm14-8h12v6H56v-6zm14 0h12v6H70v-6zm0-16h12v6H70V0zM28 32h12v6H28v-6zM14 16h12v6H14v-6zM0 24h12v6H0v-6zm0 8h12v6H0v-6zm14 0h12v6H14v-6zm14 8h12v6H28v-6zm-14 0h12v6H14v-6zm28 0h12v6H42v-6zm14-8h12v6H56v-6zm0-8h12v6H56v-6zm14 8h12v6H70v-6zm0 8h12v6H70v-6zM14 24h12v6H14v-6zm14-8h12v6H28v-6zM14 8h12v6H14V8zM0 8h12v6H0V8z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'), ('pattern3', 'url("data:image/svg+xml,%3Csvg width=\'40\' height=\'40\' viewBox=\'0 0 40 40\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M20 20.5V18H0v-2h20v-2H0v-2h20v-2H0V8h20V6H0V4h20V2H0V0h22v20h2V0h2v20h2V0h2v20h2V0h2v20h2V0h2v20h2v2H20v-1.5zM0 20h2v20H0V20zm4 0h2v20H4V20zm4 0h2v20H8V20zm4 0h2v20h-2V20zm4 0h2v20h-2V20zm4 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2zm0 4h20v2H20v-2z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'), ('pattern4', 'url("data:image/svg+xml,%3Csvg width=\'20\' height=\'20\' viewBox=\'0 0 20 20\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M0 0h20L0 20z\' fill=\'%230148fd\' fill-opacity=\'0.18\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")'), ('pattern5', 'url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'112\' height=\'92\' viewBox=\'0 0 112 92\'%3E%3Cg fill=\'%230148fd\' fill-opacity=\'0.18\'%3E%3Cpath fill-rule=\'evenodd\' d=\'M72 10H40L16 20H0v8h16l24-14h32l24 14h16v-8H96L72 10zm0-8H40L16 4H0v8h16l24-6h32l24 6h16V4H96L72 2zm0 84H40l-24-6H0v8h16l24 2h32l24-2h16v-8H96l-24 6zm0-8H40L16 64H0v8h16l24 10h32l24-10h16v-8H96L72 78zm0-12H40L16 56H0v4h16l24 14h32l24-14h16v-4H96L72 66zm0-16H40l-24-2H0v4h16l24 6h32l24-6h16v-4H96l-24 2zm0-16H40l-24 6H0v4h16l24-2h32l24 2h16v-4H96l-24-6zm0-16H40L16 32H0v4h16l24-10h32l24 10h16v-4H96L72 18z\'/%3E%3C/g%3E%3C/svg%3E")')], default='pattern1', max_length=20)),
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
            name='ProgramModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
                ('question_type', models.CharField(choices=[('AGREEMENT', 'Agreement Scale'), ('RATING', 'Rating Scale')], max_length=20)),
                ('is_required', models.BooleanField(default=True)),
                ('sentiment', models.IntegerField(choices=[(1, 'Positive'), (-1, 'Negative')], default=1)),
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
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('diagram', models.ImageField(blank=True, null=True, upload_to='diagrams/')),
                ('text_position_from_diagram', models.CharField(choices=[('above', 'Above the Diagram'), ('below', 'Below the Diagram'), ('left', 'Left of the Diagram'), ('right', 'Right of the Diagram')], default='below', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('exercise_type', models.CharField(choices=[('fill_blank', 'Fill in the Blanks'), ('short_answer', 'Short Answer'), ('multiple_choice', 'Multiple Choice')], max_length=20)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('questions', models.ManyToManyField(blank=True, related_name='exercises', to='client.exercisequestion')),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('additional_resources', models.ManyToManyField(blank=True, related_name='sections', to='client.additionalresource')),
                ('background_style', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='client.backgroundstyle')),
                ('categories', models.ManyToManyField(related_name='modules', to='client.category')),
            ],
        ),
        migrations.CreateModel(
            name='ModuleRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='client.module')),
            ],
        ),
    ]
