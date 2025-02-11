from django.shortcuts import render

# Create your views here.

def module_overview(request):
  
    progress=50

    return render(request, 'moduleOverview2.html', {'progress_value': progress})