
import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must consist at least three alphanumericals', regex='^\\w{3,}$')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('new_email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('email_verified', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.PositiveIntegerField(null=True)),
                ('gender', models.CharField(choices=[('female', 'Female'), ('male', 'Male'), ('other', 'Other'), ('N/A', 'Prefer not to say')], max_length=20, null=True)),
                ('ethnicity', models.CharField(blank=True, choices=[('asian', 'Asian'), ('black', 'Black or African Descent'), ('hispanic', 'Hispanic or Latino'), ('white', 'White or Caucasian'), ('middle_eastern', 'Middle Eastern or North African'), ('indigenous', 'Indigenous or Native'), ('south_asian', 'South Asian'), ('pacific_islander', 'Pacific Islander'), ('mixed', 'Mixed or Multiracial'), ('other', 'Other'), ('N/A', 'Prefer not to say')], max_length=50, null=True)),
                ('last_time_to_work', models.CharField(choices=[('1_month', 'In the last 1 month'), ('3_months', 'In the last 3 months'), ('6_months', 'In the last 6 months'), ('1_year', 'In the last 1 year'), ('2_years', 'In the last 2 years'), ('3_plus_years', 'More than 3 years ago'), ('never', 'Never worked before')], max_length=20, null=True)),
                ('sector', models.CharField(choices=[('it', 'Information Technology'), ('healthcare', 'Healthcare'), ('education', 'Education'), ('finance', 'Finance'), ('engineering', 'Engineering'), ('retail', 'Retail & E-commerce'), ('hospitality', 'Hospitality & Tourism'), ('marketing', 'Marketing & Advertising'), ('government', 'Government & Public Service'), ('other', 'Other')], max_length=50, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='User_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire_UserResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.questionnaire')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_value', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(-2), django.core.validators.MaxValueValidator(2)])),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.question')),
                ('user_response', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_responses', to='users.questionnaire_userresponse')),
            ],
        ),
        migrations.CreateModel(
            name='DailyQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('quote', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.quote')),
            ],
        ),
        migrations.CreateModel(
            name='StickyNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sticky_notes', to='users.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='UserModuleEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_on', models.DateTimeField(auto_now_add=True)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_users', to='client.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_enrollments', to='users.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='UserProgramEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_on', models.DateTimeField(auto_now_add=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrolled_users', to='client.program')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_enrollments', to='users.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response_text', models.TextField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='client.exercisequestion')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser')),
            ],
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('connected_with_family', models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No')], max_length=3, null=True)),
                ('expressed_gratitude', models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No')], max_length=3, null=True)),
                ('caffeine', models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No')], max_length=3, null=True)),
                ('hydration', models.PositiveIntegerField(blank=True, null=True)),
                ('goal_progress', models.CharField(blank=True, choices=[('low', 'Low'), ('moderate', 'Moderate'), ('high', 'High')], max_length=10, null=True)),
                ('outdoors', models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No')], max_length=3, null=True)),
                ('sunset', models.CharField(blank=True, choices=[('yes', 'Yes'), ('no', 'No')], max_length=3, null=True)),
                ('stress', models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], max_length=10, null=True)),
                ('sleep_hours', models.PositiveIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'date')},
            },
        ),
        migrations.CreateModel(
            name='UserExerciseProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser')),
            ],
            options={
                'unique_together': {('user', 'exercise')},
            },
        ),
        migrations.CreateModel(
            name='UserModuleProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completion_percentage', models.FloatField(default=0.0)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='client.module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_progress', to='users.enduser')),
            ],
            options={
                'unique_together': {('user', 'module')},
            },
        ),
        migrations.CreateModel(
            name='UserProgramProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completion_percentage', models.FloatField(default=0.0)),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_progress', to='client.program')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_progress', to='users.enduser')),
            ],
            options={
                'unique_together': {('user', 'program')},
            },
        ),
        migrations.CreateModel(
            name='UserResourceProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.additionalresource')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser')),
            ],
            options={
                'unique_together': {('user', 'resource')},
            },
        ),
        migrations.CreateModel(
            name='UserVideoProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In_Progress'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.enduser')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='client.videoresource')),
            ],
            options={
                'unique_together': {('user', 'video')},
            },
        ),
    ]
