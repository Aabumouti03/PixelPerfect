from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'welcome_page.html')
