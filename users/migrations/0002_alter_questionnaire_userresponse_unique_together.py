# Generated by Django 5.1.2 on 2025-03-05 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='questionnaire_userresponse',
            unique_together=set(),
        ),
    ]
