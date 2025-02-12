from django.shortcuts import render

# Create your views here.
def client_dashboard(request):
    return render(request, 'client_dashboard.html')