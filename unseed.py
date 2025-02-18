import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings") 
django.setup()

from client.models import Program, Module, Section, Exercise, ExerciseQuestion, AdditionalResource
from users.models import User, Admin, EndUser, UserProgramEnrollment, UserModuleEnrollment, UserProgramProgress, UserModuleProgress, ExerciseResponse
from django.db import connection

def unseed_data():
    print("⚠️ Deleting all seeded data except Admins and their users...")

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
        Module,
    ]

    for model in models_to_delete:
        try:
            deleted_count, _ = model.objects.all().delete()
            print(f"✅ Deleted {deleted_count} objects from {model.__name__}")
        except Exception as e:
            print(f"⚠️ Skipping {model.__name__}: {e}")

    end_users = EndUser.objects.all()
    deleted_endusers = end_users.count()

    for enduser in end_users:
        user = enduser.user
        enduser.delete()
        user.delete()

    print(f"✅ Deleted {deleted_endusers} EndUsers and their User accounts.")

    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = ON;")

    print("✅ Unseeding complete! Admins and their related users are preserved.")

if __name__ == "__main__":
    unseed_data()