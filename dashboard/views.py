from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def admin_dashboard(request):
    return render(request, 'dashboard/dashboard.html')
