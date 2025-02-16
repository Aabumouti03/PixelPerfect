from django.shortcuts import redirect, render
from django.http import HttpResponse
from .forms import UserSignUpForm, EndUserProfileForm

# Create your views here.

#A function for displaying a page that welcomes users
def welcome_page(request):
    return render(request, 'welcome_page.html')

#A function for displaying a log in page
def log_in(request):
    return render(request, 'log_in.html')

#A function for displaying a sign up page
def sign_up(request):
    if request.method == "POST":
        user_form = UserSignUpForm(request.POST)
        profile_form = EndUserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('log_in')

    else:
        user_form = UserSignUpForm()
        profile_form = EndUserProfileForm()

    return render(request, 'sign_up.html', {'user_form': user_form, 'profile_form': profile_form})

#A function for redirecting the user to the welcome page after logging out
def log_out(request):
    pass