from django.shortcuts import render
from django.http import HttpResponse
from .forms import SignUpForm

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'welcome_page.html')

#A function for displaying a log in page
def log_in(request):
    return render(request, 'log_in.html')

#A function for displaying a sign up page
def sign_up(request):
    form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})