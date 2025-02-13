from django.shortcuts import render

def welcome_view(request):
    return render(request, 'welcome.html')

def onboarding(request):
    return render(request, 'questionnaire.html')
