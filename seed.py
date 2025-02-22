import django
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")
django.setup()

# Import the correct User model
from users.models import User, EndUser, UserModuleEnrollment, UserModuleProgress
from client.models import Module, Section, Exercise, ExerciseQuestion, Program

# ✅ New modules added
MODULES_AND_SECTIONS = {
    "Exploring your work identity": {
        "description": "Understand your work motivations and identity.",
    },
    "Understanding your superpowers": {
        "description": "Finding your strengths supercharges your self-belief.",
    },
    "Exploring opportunities": {
        "description": "Motivation, where do you want to go?",
    },
    "Planning what's next": {
        "description": "Confidence PDF - what is getting in the way, personal SWOT.",
    },
    "Knowing your values": {
        "description": "Getting unstuck PDF - know your values, getting unstuck PDF - Be, do and have exercise.",
    },
}

def seed_data():
    """Seeds the database with modules, users, enrollments, and progress."""

    # ✅ Create Users
    users_data = [
        {"username": "bob", "first_name": "Bob", "last_name": "Smith", "email": "bob@example.com", "password": "password123"},
        {"username": "alice", "first_name": "Alice", "last_name": "Johnson", "email": "alice@example.com", "password": "password123"}
    ]

    created_users = []
    for user_data in users_data:
        try:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    "first_name": user_data['first_name'],
                    "last_name": user_data['last_name'],
                    "email": user_data['email'],
                }
            )
            if created:
                user.set_password(user_data['password'])  # Hash the password
                user.save()
                created_users.append(user)
                print(f"✅ Created user: {user.username}")

            # Create EndUser profile
            end_user, _ = EndUser.objects.get_or_create(
                user=user,
                defaults={
                    "age": 25,
                    "gender": "male",  # Adjust as needed
                    "last_time_to_Work": "1_year",
                    "sector": "IT"
                }
            )
        except Exception as e:
            print(f"❌ Error creating user {user_data['username']}: {e}")

    # ✅ Create Modules
    created_modules = []
    for module_title, module_data in MODULES_AND_SECTIONS.items():
        try:
            module, created = Module.objects.get_or_create(
                title=module_title,
                defaults={"description": module_data["description"]}
            )
            if created:
                print(f"✅ Created module: {module_title}")
            created_modules.append(module)
        except Exception as e:
            print(f"❌ Error creating module {module_title}: {e}")

    # ✅ Create Program and Link Modules
    try:
        program, created = Program.objects.get_or_create(
            title="Next Step",
            defaults={"description": "Figuring your next steps."}
        )

        required_modules = list(MODULES_AND_SECTIONS.keys())  # All modules in the dictionary
        existing_modules = Module.objects.filter(title__in=required_modules)

        if existing_modules.count() == len(required_modules):
            program.modules.set(existing_modules)
            print(f"✅ Program '{program.title}' linked to all modules.")
        else:
            print(f"⚠️ Warning: Not all modules exist. Skipping some program-module linking.")

    except Exception as e:
        print(f"❌ Error creating program: {e}")

    # ✅ Enroll Users in Modules
    for user in created_users:
        try:
            end_user = EndUser.objects.get(user=user)
            for module in Module.objects.all():
                UserModuleEnrollment.objects.get_or_create(user=end_user, module=module)
                UserModuleProgress.objects.get_or_create(user=end_user, module=module, completion_percentage=0, status='not_started')

            print(f"✅ User {user.username} enrolled in all modules.")
        except Exception as e:
            print(f"❌ Error enrolling user {user.username}: {e}")

    print("🎉 ✅ Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()