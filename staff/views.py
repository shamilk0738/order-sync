from django.shortcuts import render
from .models import Staff
from django.contrib.auth.models import User
def user_list(request):
    users = User.objects.all()
    return render(request, 'staff/staff_list.html', {'users': users})

