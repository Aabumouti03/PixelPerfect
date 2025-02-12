from django.shortcuts import render

# Create your views here.

def module_overview(request):
  
    progress=50

    return render(request, 'moduleOverview.html', {'progress_value': progress})