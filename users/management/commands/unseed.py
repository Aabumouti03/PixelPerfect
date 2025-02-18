from django.core.management.base import BaseCommand
from client.models import Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource
from users.models import (
    UserProgramEnrollment, UserModuleEnrollment, 
    UserProgramProgress, UserModuleProgress, ExerciseResponse
)
from django.db import connection, transaction

class Command(BaseCommand):
    help = "Safely deletes all seeded data while avoiding missing tables."

    def handle(self, *args, **kwargs):
        """Deletes all seeded data."""
        self.stdout.write("⚠️ Deleting all seeded data...")

        try:
            with transaction.atomic():  # Ensure atomicity
                # ✅ Disable foreign key constraints (SQLite/PostgreSQL fix)
                with connection.cursor() as cursor:
                    cursor.execute("PRAGMA foreign_keys = OFF;")

                models_to_delete = [
                    ExerciseResponse, ExerciseQuestion, Exercise,
                    Section, AdditionalResource, Module, Program,
                    UserProgramProgress, UserModuleProgress,
                    UserProgramEnrollment, UserModuleEnrollment
                ]

                for model in models_to_delete:
                    try:
                        deleted_count, _ = model.objects.all().delete()
                        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {deleted_count} objects from {model.__name__}"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"⚠️ Skipping {model.__name__}: {e}"))

                # ✅ Re-enable foreign key constraints
                with connection.cursor() as cursor:
                    cursor.execute("PRAGMA foreign_keys = ON;")

            self.stdout.write(self.style.SUCCESS("✅ Unseeding complete!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during unseeding: {e}"))
