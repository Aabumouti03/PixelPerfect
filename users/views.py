from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'users/dashboard.html')

def modules(request):
    return render(request, 'users/modules.html')

def profile(request):
    return render(request, 'users/profile.html')

def logout_view(request):
    return render(request, 'users/logout.html')
