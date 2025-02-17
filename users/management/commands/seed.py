from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import EndUser
from client.models import Module, Section, Exercise, ExerciseQuestion, Program
import django
import os

# ✅ Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")  # Update this if your project name is different
django.setup()

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with test users and learning modules"

    def handle(self, *args, **kwargs):
        self.seed_users()
        self.seed_modules()
        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))

    def seed_users(self):
        user_data = {
            "username": "dandoe",
            "first_name": "Dan",
            "last_name": "Doe",
            "email": "dandoe@example.org",
            "password": "Testuser123",
        }

        profile_data = {
            "age": 20,
            "gender": "male",
            "ethnicity": "asian",
            "sector": "healthcare",
            "last_time_to_work": "1_month",
            "phone_number": "11111111",
        }

        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "email": user_data["email"],
            }
        )

        if created:
            user.set_password(user_data["password"])
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
        else:
            self.stdout.write(self.style.WARNING(f"User {user.username} already exists."))

        EndUser.objects.get_or_create(user=user, defaults=profile_data)

    def seed_modules(self):
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
                    }
                ]
            }
        }

        for module_title, module_data in MODULES_AND_SECTIONS.items():
            module, _ = Module.objects.get_or_create(
                title=module_title,
                defaults={"description": module_data["description"]}
            )

            for section_data in module_data["sections"]:
                section, _ = Section.objects.get_or_create(
                    title=section_data["title"],
                    defaults={"description": section_data["description"]}
                )

                # ✅ Correctly associate the section with the module (ManyToManyField)
                module.sections.add(section)  

                for exercise_data in section_data["exercises"]:
                    exercise, _ = Exercise.objects.get_or_create(
                        title=exercise_data["title"],
                        defaults={"exercise_type": exercise_data["exercise_type"]}
                    )

                    # ✅ Associate exercise with section (ManyToMany)
                    section.exercises.add(exercise)  

                    for question_text in exercise_data["questions"]:
                        question, _ = ExerciseQuestion.objects.get_or_create(
                            question_text=question_text,
                            defaults={"has_blank": False}
                        )

                        # ✅ Correctly associate question with exercise (ManyToMany)
                        exercise.questions.add(question)

        program, _ = Program.objects.get_or_create(
            title="Next Step",
            defaults={"description": "Figuring out your next steps."}
        )

        program.modules.set(Module.objects.filter(title__in=[
            "Exploring your work identity"
        ]))

        self.stdout.write(self.style.SUCCESS("✅ Modules, Sections, Exercises, and Questions seeded successfully!"))

