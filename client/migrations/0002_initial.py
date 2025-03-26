# Generated by Django 5.1.7 on 2025-03-26 02:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulerating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser'),
        ),
        migrations.AddField(
            model_name='program',
            name='categories',
            field=models.ManyToManyField(related_name='programs', to='client.category'),
        ),
        migrations.AddField(
            model_name='programmodule',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_programs', to='client.module'),
        ),
        migrations.AddField(
            model_name='programmodule',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_modules', to='client.program'),
        ),
        migrations.AddField(
            model_name='program',
            name='modules',
            field=models.ManyToManyField(related_name='programs', through='client.ProgramModule', to='client.module'),
        ),
        migrations.AddField(
            model_name='question',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='client.category'),
        ),
        migrations.AddField(
            model_name='question',
            name='questionnaire',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='client.questionnaire'),
        ),
        migrations.AddField(
            model_name='section',
            name='exercises',
            field=models.ManyToManyField(related_name='sections', to='client.exercise'),
        ),
        migrations.AddField(
            model_name='module',
            name='sections',
            field=models.ManyToManyField(related_name='modules', to='client.section'),
        ),
        migrations.AddField(
            model_name='module',
            name='video_resources',
            field=models.ManyToManyField(blank=True, related_name='modules', to='client.videoresource'),
        ),
        migrations.AlterUniqueTogether(
            name='modulerating',
            unique_together={('module', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='programmodule',
            unique_together={('program', 'order')},
        ),
    ]
