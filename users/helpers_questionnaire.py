from collections import defaultdict
from django.shortcuts import get_object_or_404
from .models import  QuestionResponse, Questionnaire_UserResponse
from client.models import Program, Module, Category
def assess_user_responses_programs(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests programs based on significant negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested programs.
    """

    # Get latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()
    if not latest_response:
        return {}  # No responses, return empty recommendations

    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    category_scores = defaultdict(float)
    category_question_count = defaultdict(int)

    # Process each user response
    for response in user_responses:
        question = response.question
        category = question.category

        if category:  
            sentiment_multiplier = question.sentiment  # -1 for negative questions, +1 for positive questions
            rating = response.rating_value  # User response value : -2 to 2

            category_scores[category.id] += rating * sentiment_multiplier
            category_question_count[category.id] += 1 # Track number of questions per category to calculate average score

    # dividing by the number of questions per category for normalization
    normalized_category_scores = {
        category_id: (score / category_question_count[category_id])
        for category_id, score in category_scores.items()
    }

    # threshold for recommendations
    NEGATIVE_THRESHOLD = -1

    suggested_programs = {}

    for category_id, score in normalized_category_scores.items():
        if score < NEGATIVE_THRESHOLD:
            category = get_object_or_404(Category, id=category_id)

            # Recommend remedial programs for weak categories
            programs = Program.objects.filter(categories=category)
            suggested_programs[category.name] = list(programs)

    return suggested_programs


def assess_user_responses_modules(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests modules based on significant negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested modules.
    """

    # Get latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()
    if not latest_response:
        return {}  # No responses, return empty recommendations

    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    category_scores = defaultdict(float)
    category_question_count = defaultdict(int)

    # Process each user response
    for response in user_responses:
        question = response.question
        category = question.category

        if category: 
            sentiment_multiplier = question.sentiment  # -1 for negative questions, +1 for positive questions
            rating = response.rating_value  # User response value : -2 to 2

            category_scores[category.id] += rating * sentiment_multiplier
            category_question_count[category.id] += 1  # Track number of questions per category to calculate average score

    # dividing by the number of questions per category for normalization
    normalized_category_scores = {
        category_id: (score / category_question_count[category_id])
        for category_id, score in category_scores.items()
    }

    # threshold for recommendations
    NEGATIVE_THRESHOLD = -1

    suggested_modules = {}

    for category_id, score in normalized_category_scores.items():
        if score < NEGATIVE_THRESHOLD:
            category = get_object_or_404(Category, id=category_id)

            # Recommend relevant modules
            modules = Module.objects.filter(categories=category)
            suggested_modules[category.name] = list(modules)

    return suggested_modules

