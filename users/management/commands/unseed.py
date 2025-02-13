import django
import os

# ✅ Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")  # Update if your project name is different
django.setup()

from client.models import Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource
from users.models import User, Admin, EndUser, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress, ExerciseResponse
from django.db import connection

def unseed_data():
    """Safely deletes all seeded data while avoiding missing tables."""
    print("⚠️ Deleting all seeded data...")

    # ✅ Disable foreign key constraints (SQLite fix)
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")

    models_to_delete = [
        ExerciseResponse,  # User responses to exercises
        ExerciseQuestion,  # Exercise questions
        Exercise,  # Exercises inside sections
        Section,  # Sections inside modules
        AdditionalResource,  # Additional resources linked to sections
        Module,  # Modules inside programs
        Program,  # Programs
        UserProgramProgress,  # User progress tracking (program level)
        UserModuleProgress,  # User progress tracking (module level)
        UserProgramEnrollment,  # User enrollments in programs
        UserModuleEnrollment,  # User enrollments in modules
        Module,
    ]

    for model in models_to_delete:
        try:
            deleted_count, _ = model.objects.all().delete()
            print(f"✅ Deleted {deleted_count} objects from {model.__name__}")
        except Exception as e:
            print(f"⚠️ Skipping {model.__name__}: {e}")

    # ✅ Re-enable foreign key constraints
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON;")

    print("✅ Unseeding complete!")

if __name__ == "__main__":
    unseed_data()
