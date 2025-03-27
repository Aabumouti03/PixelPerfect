from django.core.management.base import BaseCommand
from django.db import connection
from client.models import Module, Program, ProgramModule, Category, Section, Exercise, ExerciseQuestion, Questionnaire, Question
from users.models import UserModuleEnrollment, UserProgramEnrollment, Quote, Admin, EndUser

class Command(BaseCommand):
    help = "Deletes all seeded data"

    def handle(self, *args, **kwargs):
        self.stdout.write("⚠️ Deleting all seeded data...")

        # 🚫 DO NOT use PRAGMA — it's for SQLite only
        # cursor.execute("PRAGMA foreign_keys = OFF;")

        with connection.cursor() as cursor:
            # 🚀 Delete in correct order to prevent foreign key conflicts
            UserModuleEnrollment.objects.all().delete()
            UserProgramEnrollment.objects.all().delete()
            ProgramModule.objects.all().delete()
            Module.objects.all().delete()
            Program.objects.all().delete()
            Category.objects.all().delete()
            Section.objects.all().delete()
            Exercise.objects.all().delete()
            ExerciseQuestion.objects.all().delete()
            Questionnaire.objects.all().delete()
            Question.objects.all().delete()
            Quote.objects.all().delete()

            EndUser.objects.all().delete()
            # Admin.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("✅ All seeded data deleted successfully."))
