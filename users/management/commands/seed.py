import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")  
django.setup()

import random
from django.contrib.auth import get_user_model
from client.models import Module, Section, Exercise, ExerciseQuestion, Program, Category, ProgramModule, BackgroundStyle, ProgramModule, Questionnaire, Question
from users.models import EndUser, Admin, UserModuleEnrollment, UserProgramEnrollment, Quote
from django.db import transaction
from django.core.management.base import BaseCommand
from client.models import BACKGROUND_IMAGE_CHOICES

User = get_user_model()
# 
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
            
            self.seed_data()
            self.seed_users()
            # self.seed_quotes()
            self.seed_questionnaire()

        self.stdout.write(self.style.SUCCESS("✅ Database seeding complete!"))

    def seed_users(self):
        """Creates 5 EndUsers with random attributes and 1 Admin."""
        # existing_users = User.objects.filter(username__startswith="EndUser").count()
        # start_index = existing_users + 1

        # for i in range(start_index, start_index + 5):
        #     username = f"EndUser{i}"
        #     email = f"enduser{i}@example.com"

        #     user, created = User.objects.get_or_create(username=username, defaults={
        #         "email": email,
        #         "is_staff": False,
        #         "is_superuser": False,
        #         "email_verified": True,
        #     })

        #     if created:
        #         user.set_password(PASSWORD)
        #         user.save()

        #         random_gender = random.choice(GENDER_OPTIONS)
        #         random_last_time_to_work = random.choice(TIME_DURATION_CHOICES)
        #         random_sector = random.choice(SECTOR_CHOICES)
        #         random_age = random.randint(18, 60)

        #         enduser = EndUser.objects.create(
        #             user=user,
        #             age=random_age,
        #             gender=random_gender,
        #             last_time_to_work=random_last_time_to_work,
        #             sector=random_sector
        #         )

        #         # Randomly assign 0 or more modules
        #         all_modules = list(Module.objects.all())
        #         num_modules = random.randint(0, len(all_modules))
        #         selected_modules = random.sample(all_modules, num_modules)
                
        #         for module in selected_modules:
        #             UserModuleEnrollment.objects.create(
        #                 user=enduser,
        #                 module=module
        #             )

        #         # Randomly assign 0 or 1 program
        #         program_enrolled = False
        #         if random.choice([True, False]) and Program.objects.exists():
        #             program = random.choice(Program.objects.all())
        #             UserProgramEnrollment.objects.create(
        #                 user=enduser,
        #                 program=program
        #             )
        #             program_enrolled = True
                    

        #         print(f" Created EndUser: {user.username} | Gender: {random_gender} | Work Gap: {random_last_time_to_work} | Sector: {random_sector}")
        #         print(f" - Enrolled in {num_modules} modules")
        #         print(f" - Program enrollment: {'Yes' if program_enrolled else 'No'}")
                

        if not Admin.objects.exists():  
            admin, created = User.objects.get_or_create(username=ADMIN["username"], defaults={
                "email": ADMIN["email"],
                "is_staff": ADMIN["is_staff"],
                "is_superuser": ADMIN["is_superuser"],
                "email_verified": True,
            })
            if created:
                admin.set_password(PASSWORD)
                admin.save()
                Admin.objects.create(user=admin)
                print(f"✅ Created Admin: {admin.username}")
        else:
            print("⚠️ Admin already exists. Skipping creation.")


    def seed_data(self):
            """Seeds the database with modules, categories, sections, exercises, and questions."""
            with transaction.atomic(): 

                # ✅ Step 1: Create Categories
                categories = {
                    "Career Development": None,
                    "Personal Growth": None,
                    "Professional Skills": None
                }

                for category_name in categories.keys():
                    category, created = Category.objects.get_or_create(name=category_name)
                    categories[category_name] = category
                    print(f"✅ Created/Updated Category: {category.name}")

                # ✅ Step 2: Create Background Styles
                background_styles = []
                for pattern_key, pattern_url in BACKGROUND_IMAGE_CHOICES:
                    background_style, created = BackgroundStyle.objects.get_or_create(
                        background_color="#73c4fd",  
                        background_image=pattern_key,  
                    )
                    background_styles.append(background_style)
                    print(f"✅ Created BackgroundStyle: {background_style.background_image}")

                # ✅ Step 3: Create Modules and Assign Categories
                for module_title, module_data in MODULES_AND_SECTIONS.items():
                    module, created = Module.objects.get_or_create(
                        title=module_title,
                        defaults={"description": module_data["description"]}
                    )

                    # Assign a random background style
                    module.background_style = random.choice(background_styles)
                    module.save()

                    # Assign a category randomly
                    random_category = random.choice(list(categories.values()))
                    module.categories.add(random_category)

                    print(f"✅ Created/Updated Module: {module.title} | Category: {random_category.name} | Background: {module.background_style.background_image}")

                    # ✅ Step 4: Create Sections for Each Module
                    for section_data in module_data["sections"]:
                        section, created = Section.objects.get_or_create(
                            title=section_data["title"],
                            defaults={"description": section_data["description"]}
                        )
                        
                        module.sections.add(section)

                        # ✅ Step 5: Create Exercises and Questions
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

                    if not module:
                        print(f"❌ Module '{module_title}' not found. Skipping.")
                        continue

                    if ProgramModule.objects.filter(program=program, order=order).exists():
                        print(f"⚠️ A module is already assigned to Program '{program.title}' at order {order}. Skipping '{module_title}'.")
                        continue

                    # Check if this module is already assigned to the program
                    if ProgramModule.objects.filter(program=program, module=module).exists():
                        print(f"⚠️ {module_title} already exists in Program '{program.title}'. Skipping.")
                        continue

                    ProgramModule.objects.create(program=program, module=module, order=order)
                    print(f"✅ Added {module_title} to Program '{program.title}' at order {order}.")


    def seed_quotes(self, *args, **kwargs):
        if Quote.objects.exists(): 
            print("⚠️ Quotes already exist. Skipping seeding.")
            return
    
        quotes = [
            {"text": "Success is not the key to happiness. Happiness is the key to success. — Albert Schweitzer"},
            {"text": "Your limitation—it’s only your imagination."},
            {"text": "Do what you can, with what you have, where you are. — Theodore Roosevelt"},
            {"text": "Dream big and dare to fail. — Norman Vaughan"},
            {"text": "Opportunities don't happen. You create them. — Chris Grosser"},
            {"text": "Don't let yesterday take up too much of today. — Will Rogers"},
            {"text": "The only way to do great work is to love what you do. — Steve Jobs"},
            {"text": "Act as if what you do makes a difference. It does. — William James"},
            {"text": "Believe you can and you're halfway there. — Theodore Roosevelt"},
            {"text": "Every day may not be good, but there's something good in every day."},
            {"text": "Keep your face always toward the sunshine—and shadows will fall behind you. — Walt Whitman"},
            {"text": "You are never too old to set another goal or to dream a new dream. — C.S. Lewis"},
            {"text": "Difficult roads often lead to beautiful destinations."},
            {"text": "You don't have to be great to start, but you have to start to be great. — Zig Ziglar"},
            {"text": "Happiness is not something ready-made. It comes from your own actions. — Dalai Lama"},
            {"text": "Work hard in silence, let your success be your noise. — Frank Ocean"},
            {"text": "Failure is simply the opportunity to begin again, this time more intelligently. — Henry Ford"},
            {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever. — Mahatma Gandhi"},
            {"text": "Start where you are. Use what you have. Do what you can. — Arthur Ashe"},
            {"text": "If you want to lift yourself up, lift up someone else. — Booker T. Washington"},
            {"text": "No one is perfect—that’s why pencils have erasers. — Wolfgang Riebe"},
            {"text": "Success is getting what you want. Happiness is wanting what you get. — Dale Carnegie"},
            {"text": "Happiness depends upon ourselves. — Aristotle"},
            {"text": "You are capable of amazing things."},
            {"text": "Do what makes your soul shine."},
            {"text": "What lies behind us and what lies before us are tiny matters compared to what lies within us. — Ralph Waldo Emerson"},
            {"text": "Don't watch the clock; do what it does. Keep going. — Sam Levenson"},
            {"text": "Small steps in the right direction can turn out to be the biggest step of your life."},
            {"text": "Happiness is a direction, not a place. — Sydney J. Harris"},
            {"text": "If opportunity doesn’t knock, build a door. — Milton Berle"},
            {"text": "The best way to predict the future is to create it. — Peter Drucker"},
            {"text": "Be kind whenever possible. It is always possible. — Dalai Lama"},
            {"text": "You were born to be real, not to be perfect."},
            {"text": "Be yourself; everyone else is already taken. — Oscar Wilde"},
            {"text": "Stay close to anything that makes you glad you are alive. — Hafiz"},
            {"text": "Enjoy the little things, for one day you may look back and realize they were the big things. — Robert Brault"},
            {"text": "Your vibe attracts your tribe."},
            {"text": "Be strong. You never know who you are inspiring."},
            {"text": "Turn your wounds into wisdom. — Oprah Winfrey"},
            {"text": "Be a voice, not an echo."},
            {"text": "With the new day comes new strength and new thoughts. — Eleanor Roosevelt"},
            {"text": "You are enough just as you are."},
            {"text": "A champion is defined not by their wins but by how they can recover when they fall. — Serena Williams"},
            {"text": "Your life only gets better when you get better."},
            {"text": "Happiness is not by chance, but by choice. — Jim Rohn"},
            {"text": "It always seems impossible until it's done. — Nelson Mandela"},
            {"text": "Do more of what makes you happy."},
            {"text": "Life isn’t about waiting for the storm to pass, it’s about learning to dance in the rain. — Vivian Greene"},
            {"text": "Success is falling nine times and getting up ten. — Jon Bon Jovi"},
            {"text": "You didn’t come this far to only come this far."},
            {"text": "Some people want it to happen, some wish it would happen, others make it happen. — Michael Jordan"},
            {"text": "Let your dreams be bigger than your fears."},
            {"text": "Doubt kills more dreams than failure ever will. — Suzy Kassem"},
            {"text": "Every day is a second chance."},
            {"text": "You are braver than you believe, stronger than you seem, and smarter than you think. — A.A. Milne"},
            {"text": "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle."},
            {"text": "Never bend your head. Always hold it high. Look the world straight in the eye. — Helen Keller"},
            {"text": "Be the reason someone smiles today."},
            {"text": "Rise above the storm and you will find the sunshine. — Mario Fernandez"},
            {"text": "Take the risk or lose the chance."},
            {"text": "Happiness is letting go of what you think your life is supposed to look like."},
            {"text": "A goal without a plan is just a wish. — Antoine de Saint-Exupéry"},
            {"text": "Keep going. Everything you need will come to you at the perfect time."},
            {"text": "You are stronger than you think."},
            {"text": "The only thing you can control is your own effort."},
            {"text": "Wake up with determination, go to bed with satisfaction."},
            {"text": "Make today so awesome that yesterday gets jealous."},
            {"text": "Trust the timing of your life."},
            {"text": "Everything you can imagine is real. — Pablo Picasso"},
            {"text": "What consumes your mind, controls your life."},
            {"text": "Stay positive, work hard, make it happen."},
            {"text": "Hardships often prepare ordinary people for an extraordinary destiny. — C.S. Lewis"},
            {"text": "Kindness is a language which the deaf can hear and the blind can see. — Mark Twain"},
            {"text": "The more you give away, the more happy you become. — Dalai Lama"},
            {"text": "Light tomorrow with today. — Elizabeth Barrett Browning"},
            {"text": "Sometimes when you're in a dark place you think you've been buried, but you've actually been planted. — Christine Caine"},
            {"text": "Do what is right, not what is easy."},
            {"text": "Learn as if you will live forever, live like you will die tomorrow. — Mahatma Gandhi"},
            {"text": "Nothing is impossible, the word itself says 'I'm possible!' — Audrey Hepburn"},
            {"text": "Success usually comes to those who are too busy to be looking for it. — Henry David Thoreau"},
            {"text": "Start where you are. Use what you have. Do what you can. — Arthur Ashe"},
            {"text": "It is during our darkest moments that we must focus to see the light. — Aristotle"},
            {"text": "Act as if what you do makes a difference. It does. — William James"},
            {"text": "Opportunities don’t happen, you create them. — Chris Grosser"},
            {"text": "The best way to get started is to quit talking and begin doing. — Walt Disney"},
            {"text": "The secret of getting ahead is getting started. — Mark Twain"},
            {"text": "The only limit to our realization of tomorrow is our doubts of today. — Franklin D. Roosevelt"},
            {"text": "Whatever the mind can conceive and believe, it can achieve. — Napoleon Hill"},
        ]


        for quote in quotes:
            Quote.objects.get_or_create(text=quote["text"])

        self.stdout.write(self.style.SUCCESS("Successfully loaded quotes"))

    def seed_questionnaire(self):

        """Seeds a questionnaire with 3 questions if not already seeded. Ensures only one is active."""
        title = "Are you ready to return to work"

        questionnaire = Questionnaire.objects.filter(title=title).first()

        if questionnaire:
            existing_questions = questionnaire.questions.count()
            if existing_questions >= 3:
                print(f"⚠️ Questionnaire '{title}' already seeded with {existing_questions} questions. Skipping.")
            else:
                print(f"🔁 Questionnaire '{title}' exists but has only {existing_questions} questions. Re-seeding missing ones.")
        else:
            # ✅ Create new questionnaire and make it active
            # But first deactivate all others to enforce uniqueness
            Questionnaire.objects.all().update(is_active=False)

            questionnaire = Questionnaire.objects.create(
                title=title,
                description="A quick check-in to help you reflect on your readiness to return to work.",
                is_active=True
            )
            print(f"Created Questionnaire '{title}' and set as active")

        # If it's not active (due to a logic error or manual override), make it the ONLY active one
        if not questionnaire.is_active:
            Questionnaire.objects.exclude(id=questionnaire.id).update(is_active=False)
            questionnaire.is_active = True
            questionnaire.save()
            print(f"⚙️ Set Questionnaire '{title}' as active (after override protection)")

        # Map categories
        categories_map = {
            "Career Development": Category.objects.get(name="Career Development"),
            "Personal Growth": Category.objects.get(name="Personal Growth"),
            "Professional Skills": Category.objects.get(name="Professional Skills"),
        }

        questions_data = [
            {
                "text": "I feel confident about my career direction.",
                "category": categories_map["Career Development"],
                "sentiment": 1,
                "question_type": "AGREEMENT"
            },
            {
                "text": "I often doubt my ability to grow personally.",
                "category": categories_map["Personal Growth"],
                "sentiment": -1,
                "question_type": "RATING"
            },
            {
                "text": "I am well-prepared with the professional skills required for my next role.",
                "category": categories_map["Professional Skills"],
                "sentiment": 1,
                "question_type": "AGREEMENT"
            }
        ]

        #Add questions (only if they don't exist already)
        for q_data in questions_data:
            question, created = Question.objects.get_or_create(
                questionnaire=questionnaire,
                question_text=q_data["text"],
                defaults={
                    "question_type": q_data["question_type"],
                    "is_required": True,
                    "category": q_data["category"],
                    "sentiment": q_data["sentiment"]
                }
            )
            if created:
                print(f"   ➕ Added Question: {q_data['text'][:50]}...")

        print(f"✅ Questionnaire '{questionnaire.title}' seeded successfully and marked as active.")