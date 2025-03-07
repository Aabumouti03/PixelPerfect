import django
import os
from django.core.management.base import BaseCommand
from django.db import transaction, connection
from client.models import Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource
from users.models import EndUser, User, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress, ExerciseResponse

class Command(BaseCommand):
    help = "Deletes all seeded data except Admins and their users"
# 
    def handle(self, *args, **kwargs):
        self.stdout.write("⚠️ Deleting all seeded data...")

        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = OFF;")

            models_to_delete = [
                ExerciseResponse,
                ExerciseQuestion,
                Exercise,
                Section,
                AdditionalResource,
                Module,
                Program,
                UserProgramProgress,
                UserModuleProgress,
                UserProgramEnrollment,
                UserModuleEnrollment,
            ]

            for model in models_to_delete:
                try:
                    deleted_count, _ = model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_count} objects from {model.__name__}"))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Skipping {model.__name__}: {e}"))

            end_users = EndUser.objects.all()
            deleted_endusers = end_users.count()

            for enduser in end_users:
                user = enduser.user
                enduser.delete()
                user.delete()

            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_endusers} EndUsers and their User accounts."))

            with connection.cursor() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON;")

        self.stdout.write(self.style.SUCCESS("✅ Unseeding complete! Admins and their related users are preserved."))