from django.shortcuts import render
from users.models import EndUser

# Create your views here.
def client_dashboard(request):
    return render(request, 'client_dashboard.html')

def users_management(request):
    users = EndUser.objects.all()
    return render(request, 'users_management.html', {'users': users})