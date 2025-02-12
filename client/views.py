from django.shortcuts import render

# Create your views here.

def module_overview(request):
  
    progress=50

    return render(request, 'moduleOverview2.html', {'progress_value': progress})

def user_modules(request):
    modules = [
        {"title": "Mindfulness for a Balanced Life", "description": "Explore meditation, breathing exercises, and mental relaxation techniques to improve overall well-being.", "progress": 25},
        {"title": "Workplace Safety & Adaptation", "description": "Covers health protocols, ergonomic setups, and adjustments to the work environment.", "progress": 82},
        {"title": "Effective Communication & Collaboration", "description": "Focuses on rebuilding teamwork, trust, and clear workplace communication.", "progress": 9},
        {"title": "Time Management & Productivity", "description": "Provides strategies for balancing tasks, avoiding burnout, and staying efficient.", "progress": 47},
    ]
    return render(request, 'userModules.html', {"modules": modules})

def all_modules(request):
    all_modules = [
        {"title": "Mindfulness for a Balanced Life", "description": "Explore meditation, breathing exercises, and mental relaxation techniques to improve overall well-being.", "progress": 25},
        {"title": "Workplace Safety & Adaptation", "description": "Covers health protocols, ergonomic setups, and adjustments to the work environment.", "progress": 82},
        {"title": "Effective Communication & Collaboration", "description": "Focuses on rebuilding teamwork, trust, and clear workplace communication.", "progress": 9},
        {"title": "Time Management & Productivity", "description": "Provides strategies for balancing tasks, avoiding burnout, and staying efficient.", "progress": 47},
        {"title": "Leadership & Emotional Intelligence", "description": "Develop leadership skills, empathy, and team motivation strategies.", "progress": 64},
        {"title": "Remote Work Best Practices", "description": "Learn how to stay productive while working remotely.", "progress": 38},
        {"title": "Mental Health & Workplace Well-being", "description": "Gain awareness of workplace mental health and stress management techniques.", "progress": 55},
        {"title": "Breaking the Stigma: Mental Health Awareness", "description": "A module focusing on reducing workplace stigma around mental health.", "progress": 15},
    ]
    return render(request, 'allModules.html', {"all_modules": all_modules})