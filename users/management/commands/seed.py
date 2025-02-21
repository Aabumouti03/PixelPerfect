import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")  
django.setup()

import random
from django.contrib.auth import get_user_model
from client.models import Module, Section, Exercise, ExerciseQuestion, Program, ProgramModule
from users.models import EndUser, Admin, UserModuleEnrollment, UserProgramEnrollment
from client.models import Module, Section, Exercise, ExerciseQuestion, Program, BackgroundStyle
from django.db import transaction
from django.core.management.base import BaseCommand
from client.models import BACKGROUND_IMAGE_CHOICES

User = get_user_model()

# User Data
USERS = [
    {"username": f"EndUser{i}", "email": f"enduser{i}@example.com", "is_staff": False, "is_superuser": False}
    for i in range(1, 6)
]
ADMIN = {"username": "SuperUser", "email": "admin@example.com", "is_staff": True, "is_superuser": True}
PASSWORD = "123password"

GENDER_OPTIONS = [choice[0] for choice in EndUser.GENDER_OPTIONS]
TIME_DURATION_CHOICES = [choice[0] for choice in EndUser.TIME_DURATION_CHOICES]
SECTOR_CHOICES = [choice[0] for choice in EndUser.SECTOR_CHOICES]

MODULES_AND_SECTIONS = {
    "Exploring your work identity": {
        "description": "Understand your work motivations and identity.",
        "sections": [
            {
                "title": "Where are you now?",
                "description": "Reflect on your current work status and aspirations.",
                "exercises": [
                    {
                        "title": "Where are you now?",
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
                        "title": " Your best possible self",
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

    "Knowing your values": {
        "description": "Explore your core values and how they align with work.",
        "sections": [
            {
                "title": "Know your values",
                "description": "Identify personal values and their role in decision-making.",
                "exercises": [
                    {
                        "title": "Know your values",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What do my core values mean to me?",
                            "How will I know my work is aligned with my values? How will this feel?",
                            "How can you use your values to evaluate your career/role options right now?"
                        ]
                    }
                ]
            },
            {
                "title": "Be, do and have",
                "description": "Define what you want to achieve in life and career.",
                "exercises": [
                    {
                        "title": "Be, do and have exercise",
                        "exercise_type": "short_answer",
                        "questions": [
                            "Write down all the things that you want to BE, DO or HAVE at work",
                            "Write in one brief sentence why you want to BE, DO, HAVE each item on your list",
                            "Decide on the most important 5 areas",
                            "Take each and turn it into a goal"
                        ]
                    }
                ]
            }
        ]
    },

    "Understanding your superpowers": {
        "description": "Recognize your strengths and build self-belief.",
        "sections": [
            {
                "title": "Finding your strengths",
                "description": "Discover your natural talents and skills.",
                "exercises": [
                    {
                        "title": "Finding your strengths",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What do you have a natural talent for?",
                            "What strengths would your colleagues say you have?",
                            "Which of your strengths give you energy?",
                            "Which strengths fall in all three of these circles?",
                            "How can you use your strengths to get to where you want to be?"
                        ]
                    }
                ]
            },
            {
                "title": "Supercharge your self-belief",
                "description": "Enhance confidence through mindset and habits.",
                "exercises": [
                    {
                        "title": "Supercharge your self-belief",
                        "exercise_type": "short_answer",
                        "questions": [
                            "Think about a time you achieved something you were really proud of, what did you learn from it?",
                            "Who and what can help you get closer to your career goal?",
                            "Where are you investing your time and energy?",
                            "What positive feedback have you received?",
                            "What would you like to be telling yourself when you hit a low point or lose motivation?"
                        ]
                    }
                ]
            }
        ]
    },

    "Exploring opportunities": {
        "description": "Evaluate potential career and personal development paths.",
        "sections": [
            {
                "title": "Where do you want to go?",
                "description": "Define success and future career aspirations.",
                "exercises": [
                    {
                        "title": "Where do you want to go",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What does your career look like?",
                            "What achievements are you most proud of?",
                            "On what and with who are you spending your time?",
                            "What have been the hardest moments?",
                            "What did you have to do to get to this stage in your career?",
                            "Who and what helped you get here?",
                            "What have you overcome that you thought was impossible?",
                            "Now, what will you do with this information?"
                        ]
                    }
                ]
            }
        ]
    },

    "Planning what's next": {
        "description": "Create a structured plan for personal and professional growth.",
        "sections": [
            {
                "title": "What is getting in the way?",
                "description": "Identify barriers and strategies to overcome them.",
                "exercises": [
                    {
                        "title": "What is getting in the way",
                        "exercise_type": "short_answer",
                        "questions": [
                            "What is the story you are telling yourself that is getting in the way right now?",
                            "What would happen if you didn’t?",
                            "What stops you?",
                            "How will I change my story based on this?"
                        ]
                    }
                ]
            },
            {
                "title": "Personal SWOT",
                "description": "Analyze strengths, weaknesses, opportunities, and threats.",
                "exercises": [
                    {
                        "title": "Personal SWOT",
                        "exercise_type": "short_answer",
                        "questions": [
                            "Write down 3 strengths that you have.",
                            "When you are performing at your best, what do you notice about yourself?",
                            "What do you have a natural talent for?",
                            "Where do you see your areas for development?",
                            "What area do you know you could use some additional knowledge?",
                            "What opportunities would you like to create for yourself?",
                            "What is the most obvious opportunity that you could take advantage of?",
                            "What external factors cause you concern?",
                            "What has created a threat for you in the past?"
                        ]
                    }
                ]
            }
        ]
    }
}

class Command(BaseCommand):
    help = "Seeds the database with initial data"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting database seeding...")

        with transaction.atomic():
            self.seed_users()
            self.seed_data()

        self.stdout.write(self.style.SUCCESS("✅ Database seeding complete!"))

    def seed_users(self):
        """Creates 5 EndUsers with random attributes and 1 Admin."""
        existing_users = User.objects.filter(username__startswith="EndUser").count()
        start_index = existing_users + 1

        for i in range(start_index, start_index + 5):
            username = f"EndUser{i}"
            email = f"enduser{i}@example.com"

            user, created = User.objects.get_or_create(username=username, defaults={
                "email": email,
                "is_staff": False,
                "is_superuser": False,
            })

            if created:
                user.set_password(PASSWORD)
                user.save()

                random_gender = random.choice(GENDER_OPTIONS)
                random_last_time_to_work = random.choice(TIME_DURATION_CHOICES)
                random_sector = random.choice(SECTOR_CHOICES)
                random_age = random.randint(18, 60)

                enduser = EndUser.objects.create(
                    user=user,
                    age=random_age,
                    gender=random_gender,
                    last_time_to_work=random_last_time_to_work,
                    sector=random_sector
                )

                # Randomly assign 0 or more modules
                all_modules = list(Module.objects.all())
                num_modules = random.randint(0, len(all_modules))
                selected_modules = random.sample(all_modules, num_modules)
                
                for module in selected_modules:
                    UserModuleEnrollment.objects.create(
                        user=enduser,
                        module=module
                    )

                # Randomly assign 0 or 1 program
                program_enrolled = False
                if random.choice([True, False]) and Program.objects.exists():
                    program = random.choice(Program.objects.all())
                    UserProgramEnrollment.objects.create(
                        user=enduser,
                        program=program
                    )
                    program_enrolled = True
                    

                print(f" Created EndUser: {user.username} | Gender: {random_gender} | Work Gap: {random_last_time_to_work} | Sector: {random_sector}")
                print(f" - Enrolled in {num_modules} modules")
                print(f" - Program enrollment: {'Yes' if program_enrolled else 'No'}")
                

        if not Admin.objects.exists():  
            admin, created = User.objects.get_or_create(username=ADMIN["username"], defaults={
                "email": ADMIN["email"],
                "is_staff": ADMIN["is_staff"],
                "is_superuser": ADMIN["is_superuser"],
            })
            if created:
                admin.set_password(PASSWORD)
                admin.save()
                Admin.objects.create(user=admin)
                print(f"✅ Created Admin: {admin.username}")
        else:
            print("⚠️ Admin already exists. Skipping creation.")


    def seed_data(self):
        """Seeds the database with modules, sections, exercises, and questions."""
        with transaction.atomic(): 

            background_styles = []
            for pattern_key, pattern_url in BACKGROUND_IMAGE_CHOICES:
                background_style, created = BackgroundStyle.objects.get_or_create(
                    background_color="#73c4fd",  
                    background_image=pattern_key,  
                )
                background_styles.append(background_style)
                print(f"✅ Created BackgroundStyle: {background_style.background_image}")

            for module_title, module_data in MODULES_AND_SECTIONS.items():
                module, created = Module.objects.get_or_create(
                    title=module_title,
                    defaults={"description": module_data["description"]}
                )

                random_background_style = random.choice(background_styles)
                module.background_style = random_background_style
                module.save()

                print(f"✅ Created/Updated Module: {module.title} | Background: {random_background_style.background_image}")

                for section_data in module_data["sections"]:
                    section, created = Section.objects.get_or_create(
                        title=section_data["title"],
                        defaults={"description": section_data["description"]}
                    )
                    
                    if section.title == "Personal SWOT":
                        section.diagram = "diagrams/swot_diagram.png"  # Path in media folder
                        section.save()
                        print(f"✅ Added SWOT Diagram to Section: {section.title}")

                    module.sections.add(section)

                    for exercise_data in section_data["exercises"]:
                        exercise, created = Exercise.objects.get_or_create(
                            title=exercise_data["title"],
                            defaults={"exercise_type": exercise_data["exercise_type"]}
                        )
                        
                        section.exercises.add(exercise)

                        for question_text in exercise_data["questions"]:
                            question, created = ExerciseQuestion.objects.get_or_create(
                                question_text=question_text,
                                defaults={"has_blank": False}
                            )
                            
                            exercise.questions.add(question)

            program, created = Program.objects.get_or_create(
                title="Next Step",
                defaults={"description": "Figuring your next steps."}
            )
            
            modules_to_add = [
                ("Exploring opportunities", 1),
                ("Exploring your work identity", 2),
                ("Planning what's next", 3)
            ]

            for module_title, order in modules_to_add:
                module = Module.objects.filter(title=module_title).first()
                if module and not ProgramModule.objects.filter(program=program, module=module).exists():  
                    ProgramModule.objects.create(program=program, module=module, order=order)  
                    print(f"✅ Added {module_title} to Program 'Next Step' at order {order}.")
                else:
                    print(f"⚠️ {module_title} already exists in Program 'Next Step'. Skipping.")

        print("✅ Modules, Sections, Exercises, and Questions seeded successfully!")
