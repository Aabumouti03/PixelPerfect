#import django
#import os
# # ✅ Set up Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rework.settings")  # Update this if your project name is different
# django.setup()

# from client.models import Module, Section, Exercise, ExerciseQuestion, Program

# # ✅ Data Structure for Seeding
# MODULES_AND_SECTIONS = {
#     "Exploring your work identity": {
#         "description": "Understand your work motivations and identity.",
#         "sections": [
#             {
#                 "title": "Where are you now?",
#                 "description": "Reflect on your current work status and aspirations.",
#                 "exercises": [
#                     {
#                         "title": "Motivation PDF - where are you now?",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What are you putting up with at the moment?",
#                             "What do you think you should be doing right now, professionally?",
#                             "What do you really want in your professional life?",
#                             "What did you learn from this exercise?"
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "title": "Your best possible self",
#                 "description": "Visualize and plan your ideal professional future.",
#                 "exercises": [
#                     {
#                         "title": "Getting unstuck PDF - your best possible self",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What did you do to make this happen?",
#                             "What personal qualities did you use?",
#                             "What did you have to work on?",
#                             "Who helped you get to this point?",
#                             "What resources made the difference?"
#                         ]
#                     }
#                 ]
#             }
#         ]
#     },

#     "Knowing your values": {
#         "description": "Explore your core values and how they align with work.",
#         "sections": [
#             {
#                 "title": "Know your values",
#                 "description": "Identify personal values and their role in decision-making.",
#                 "exercises": [
#                     {
#                         "title": "Getting unstuck PDF - know your values",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What do my core values mean to me?",
#                             "How will I know my work is aligned with my values? How will this feel?",
#                             "How can you use your values to evaluate your career/role options right now?"
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "title": "Be, do and have",
#                 "description": "Define what you want to achieve in life and career.",
#                 "exercises": [
#                     {
#                         "title": "Getting unstuck PDF - Be, do and have exercise",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "Write down all the things that you want to BE, DO or HAVE at work",
#                             "Write in one brief sentence why you want to BE, DO, HAVE each item on your list",
#                             "Decide on the most important 5 areas",
#                             "Take each and turn it into a goal"
#                         ]
#                     }
#                 ]
#             }
#         ]
#     },

#     "Understanding your superpowers": {
#         "description": "Recognize your strengths and build self-belief.",
#         "sections": [
#             {
#                 "title": "Finding your strengths",
#                 "description": "Discover your natural talents and skills.",
#                 "exercises": [
#                     {
#                         "title": "Motivation PDF - finding your strengths",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What do you have a natural talent for?",
#                             "What strengths would your colleagues say you have?",
#                             "Which of your strengths give you energy?",
#                             "Which strengths fall in all three of these circles?",
#                             "How can you use your strengths to get to where you want to be?"
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "title": "Supercharge your self-belief",
#                 "description": "Enhance confidence through mindset and habits.",
#                 "exercises": [
#                     {
#                         "title": "Supercharge your self-belief",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "Think about a time you achieved something you were really proud of, what did you learn from it?",
#                             "Who and what can help you get closer to your career goal?",
#                             "Where are you investing your time and energy?",
#                             "What positive feedback have you received?",
#                             "What would you like to be telling yourself when you hit a low point or lose motivation?"
#                         ]
#                     }
#                 ]
#             }
#         ]
#     },

#     "Exploring opportunities": {
#         "description": "Evaluate potential career and personal development paths.",
#         "sections": [
#             {
#                 "title": "Where do you want to go?",
#                 "description": "Define success and future career aspirations.",
#                 "exercises": [
#                     {
#                         "title": "Motivation PDF - where do you want to go",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What does your career look like?",
#                             "What achievements are you most proud of?",
#                             "On what and with who are you spending your time?",
#                             "What have been the hardest moments?",
#                             "What did you have to do to get to this stage in your career?",
#                             "Who and what helped you get here?",
#                             "What have you overcome that you thought was impossible?",
#                             "Now, what will you do with this information?"
#                         ]
#                     }
#                 ]
#             }
#         ]
#     },

#     "Planning what's next": {
#         "description": "Create a structured plan for personal and professional growth.",
#         "sections": [
#             {
#                 "title": "What is getting in the way?",
#                 "description": "Identify barriers and strategies to overcome them.",
#                 "exercises": [
#                     {
#                         "title": "Confidence PDF - what is getting in the way",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "What is the story you are telling yourself that is getting in the way right now?",
#                             "What would happen if you didn’t?",
#                             "What stops you?",
#                             "How will I change my story based on this?"
#                         ]
#                     }
#                 ]
#             },
#             {
#                 "title": "Personal SWOT",
#                 "description": "Analyze strengths, weaknesses, opportunities, and threats.",
#                 "exercises": [
#                     {
#                         "title": "Personal SWOT",
#                         "exercise_type": "short_answer",
#                         "questions": [
#                             "Write down 3 strengths that you have.",
#                             "When you are performing at your best, what do you notice about yourself?",
#                             "What do you have a natural talent for?",
#                             "Where do you see your areas for development?",
#                             "What area do you know you could use some additional knowledge?",
#                             "What opportunities would you like to create for yourself?",
#                             "What is the most obvious opportunity that you could take advantage of?",
#                             "What external factors cause you concern?",
#                             "What has created a threat for you in the past?"
#                         ]
#                     }
#                 ]
#             }
#         ]
#     }
# }


# def seed_data():
#     """Seeds the database with modules, sections, exercises, and questions."""
#     for module_title, module_data in MODULES_AND_SECTIONS.items():
        
#         module, _ = Module.objects.get_or_create(
#             title=module_title,
#             defaults={"description": module_data["description"]}
#         )

#         for section_data in module_data["sections"]:
            
#             section, _ = Section.objects.get_or_create(
#                 title=section_data["title"],
#                 defaults={"description": section_data["description"]}
#             )

            
#             module.sections.add(section)

#             for exercise_data in section_data["exercises"]:
                
#                 exercise, _ = Exercise.objects.get_or_create(
#                     title=exercise_data["title"],
#                     defaults={"exercise_type": exercise_data["exercise_type"]}
#                 )

                
#                 section.exercises.add(exercise)

#                 for question_text in exercise_data["questions"]:
                    
#                     question, _ = ExerciseQuestion.objects.get_or_create(
#                         question_text=question_text,
#                         defaults={"has_blank": False}  # Adjust as needed
#                     )

                    
#                     exercise.questions.add(question)


#     program, created = Program.objects.get_or_create(
#         title="Next Step",
#         defaults={"description": "Figuring your next steps."}
#     )

    
#     program.modules.set([
#     Module.objects.get(title="Exploring opportunities"),
#     Module.objects.get(title="Exploring your work identity"),
#     Module.objects.get(title="Planning what's next")
#     ])


#     print("✅ Modules, Sections, Exercises, and Questions seeded successfully!")


# if __name__ == "__main__":
#     seed_data()
