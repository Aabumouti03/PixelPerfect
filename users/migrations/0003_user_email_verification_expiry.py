# Generated by Django 5.1.6 on 2025-03-11 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_email_verified_user_new_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email_verification_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
