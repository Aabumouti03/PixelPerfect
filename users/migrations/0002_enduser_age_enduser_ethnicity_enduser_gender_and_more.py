# Generated by Django 5.1.2 on 2025-02-12 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enduser',
            name='age',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='ethnicity',
            field=models.CharField(blank=True, choices=[('asian', 'Asian'), ('black', 'Black or African Descent'), ('hispanic', 'Hispanic or Latino'), ('white', 'White or Caucasian'), ('middle_eastern', 'Middle Eastern or North African'), ('indigenous', 'Indigenous or Native'), ('south_asian', 'South Asian'), ('pacific_islander', 'Pacific Islander'), ('mixed', 'Mixed or Multiracial'), ('other', 'Other'), ('N/A', 'Prefer not to say')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='gender',
            field=models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other'), ('N/A', 'Prefer not to say')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='last_time_to_Work',
            field=models.CharField(choices=[('1_month', 'In the last 1 month'), ('3_months', 'In the last 3 months'), ('6_months', 'In the last 6 months'), ('1_year', 'In the last 1 year'), ('2_years', 'In the last 2 years'), ('3_plus_years', 'More than 3 years ago'), ('never', 'Never worked before')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='sector',
            field=models.CharField(choices=[('it', 'Information Technology'), ('healthcare', 'Healthcare'), ('education', 'Education'), ('finance', 'Finance'), ('engineering', 'Engineering'), ('retail', 'Retail & E-commerce'), ('hospitality', 'Hospitality & Tourism'), ('marketing', 'Marketing & Advertising'), ('government', 'Government & Public Service'), ('other', 'Other')], max_length=50, null=True),
        ),
    ]
