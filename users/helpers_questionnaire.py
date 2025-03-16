from .models import Program, QuestionResponse, Questionnaire_UserResponse
from client.models import Program, Module, Category
from collections import defaultdict

from django.shortcuts import get_object_or_404
def assess_user_responses_programs(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests programs based on negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested programs.
    """

    # Step 1: Get the latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()

    if not latest_response:
        return {}  # No responses, return empty recommendations

    # Step 2: Fetch all responses from the latest questionnaire submission
    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    # Step 3: Reset category scores for this new response
    category_scores = defaultdict(int)

    # Step 4: Calculate scores for each category
    for response in user_responses:
        question = response.question  # Get the related question
        category = question.category  # Get the category

        if category:  # Ensure question has a category
            adjusted_score = response.rating_value * question.sentiment  # Multiply response by sentiment
            category_scores[category.id] += adjusted_score  # Update category score

    # Step 5: Find categories with negative scores
    low_score_categories = [category_id for category_id, score in category_scores.items() if score < 0]

    # Step 6: Fetch programs from the negatively scored categories
    suggested_programs = {}
    for category_id in low_score_categories:
        category = get_object_or_404(Category, id=category_id)
        programs = Program.objects.filter(categories=category)  
        suggested_programs[category.name] = list(programs)  # Convert queryset to list

    return suggested_programs

def assess_user_responses_modules(user):
    """
    Evaluates the user's latest questionnaire responses, calculates scores for each category, 
    and suggests programs based on negative scores.

    Args:
        user (EndUser): The user whose responses will be assessed.

    Returns:
        dict: A dictionary where keys are category names and values are lists of suggested programs.
    """

    # Step 1: Get the latest questionnaire response for the user
    latest_response = Questionnaire_UserResponse.objects.filter(user=user).order_by('-started_at').first()

    if not latest_response:
        return {}  # No responses, return empty recommendations

    # Step 2: Fetch all responses from the latest questionnaire submission
    user_responses = QuestionResponse.objects.filter(user_response=latest_response).select_related('question__category')

    # Step 3: Reset category scores for this new response
    category_scores = defaultdict(int)

    # Step 4: Calculate scores for each category
    for response in user_responses:
        question = response.question  # Get the related question
        category = question.category  # Get the category

        if category:  # Ensure question has a category
            adjusted_score = response.rating_value * question.sentiment  # Multiply response by sentiment
            category_scores[category.id] += adjusted_score  # Update category score

    # Step 5: Find categories with negative scores
    low_score_categories = [category_id for category_id, score in category_scores.items() if score < 0]

    # Step 6: Fetch programs from the negatively scored categories
    suggested_modules = {}
    for category_id in low_score_categories:
        category = get_object_or_404(Category, id=category_id)
        modules = Module.objects.filter(categories=category)  
        suggested_modules[category.name] = list(modules)  # Convert queryset to list

    return suggested_modules

