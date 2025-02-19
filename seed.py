import django
import os

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")
django.setup()

from django.contrib.auth.models import User
from client.models import Module, Section, Exercise, ExerciseQuestion, Program
from users.models import EndUser, UserModuleEnrollment, UserModuleProgress

# Data structure for seeding
MODULES_AND_SECTIONS = {
    "Exploring your work identity": {
        "description": "Understand your work motivations and identity.",
        "sections": [
            {
                "title": "Where are you now?",
                "description": "Reflect on your current work status and aspirations.",
                "exercises": [
                    {
                        "title": "Motivation PDF - where are you now?",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What are you putting up with at the moment?",
                            "What do you think you should be doing right now, professionally?",
                            "What do you really want in your professional life?",
                            "What did you learn from this exercise?"
                        ]
                    }
                ]
            },
            {
                "title": "Your best possible self",
                "description": "Visualize and plan your ideal professional future.",
                "exercises": [
                    {
                        "title": "Getting unstuck PDF - your best possible self",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What did you do to make this happen?",
                            "What personal qualities did you use?",
                            "What did you have to work on?",
                            "Who helped you get to this point?",
                            "What resources made the difference?"
                        ]
                    }
                ]
            }
        ]
    },
}

def seed_data():
    """Seeds the database with modules, sections, exercises, questions, users, and enrollments."""
    
    # Define users
    users = [
        {"username": "bob", "first_name": "Bob", "last_name": "Smith", "email": "bob@example.com", "password": "password123"},
        {"username": "alice", "first_name": "Alice", "last_name": "Johnson", "email": "alice@example.com", "password": "password123"}
    ]

    created_users = []
    
    # Create users and associated EndUsers
    for user_data in users:
        try:
            # Ensure password is hashed
            user = User.objects.create_user(
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                password=user_data['password']  # password will be hashed automatically
            )
            created_users.append(user)

            # Create corresponding EndUser profile with additional info
            end_user = EndUser.objects.create(
                user=user,
                age=25,
                gender='male',  # Or 'female', or 'other' as needed
                last_time_to_Work='1_year',  # Or your required value
                sector='it',  # Your choice of sector
            )

            print(f"Created User: {user.username}, EndUser: {end_user.user.username}")  # Debugging line
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")  # Debugging line

    # Create and link modules, sections, exercises, questions, and program (same as you had)
    for module_title, module_data in MODULES_AND_SECTIONS.items():
        try:
            module, _ = Module.objects.get_or_create(
                title=module_title,
                defaults={"description": module_data["description"]}
            )

            for section_data in module_data["sections"]:
                section, _ = Section.objects.get_or_create(
                    title=section_data["title"],
                    defaults={"description": section_data["description"]}
                )

                module.sections.add(section)

                for exercise_data in section_data["exercises"]:
                    exercise, _ = Exercise.objects.get_or_create(
                        title=exercise_data["title"],
                        defaults={"exercise_type": exercise_data["exercise_type"]}
                    )

                    section.exercises.add(exercise)

                    for question_text in exercise_data["questions"]:
                        question, _ = ExerciseQuestion.objects.get_or_create(
                            question_text=question_text,
                            defaults={"has_blank": False}  # Adjust as needed
                        )

                        exercise.questions.add(question)
        except Exception as e:
            print(f"Error creating module/section: {module_title}, {e}")

    # Create Program and link modules
    try:
        program, created = Program.objects.get_or_create(
            title="Next Step",
            defaults={"description": "Figuring your next steps."}
        )

        program.modules.set([
            Module.objects.get(title="Exploring opportunities"),
            Module.objects.get(title="Exploring your work identity"),
            Module.objects.get(title="Planning what's next")
        ])
    except Exception as e:
        print(f"Error creating program: {e}")

    # Enroll Users in modules
    for user in created_users:
        try:
            end_user = EndUser.objects.get(user=user)
            for module in Module.objects.all():
                # Enroll the user in the module
                UserModuleEnrollment.objects.get_or_create(user=end_user, module=module)

                # Set user progress for each module
                UserModuleProgress.objects.get_or_create(user=end_user, module=module, completion_percentage=0, status='not_started')

            print(f"User {user.username} enrolled in modules.")
        except Exception as e:
            print(f"Error enrolling user {user.username}: {e}")  # Debugging line

    print("✅ Modules, Sections, Exercises, Questions, Users, and Enrollments seeded successfully!")

if __name__ == "__main__":
    seed_data()
