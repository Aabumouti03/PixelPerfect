from django.shortcuts import render

# Create your views here.

def dashboard(request):
    return render(request, 'dashboard.html')

def modules(request):
    return render(request, 'modules.html')

def users(request):
    return render(request, 'users.html')

def programs(request):
    return render(request, 'programs.html')

def logout_view(request):
    return render(request, 'logout.html')
