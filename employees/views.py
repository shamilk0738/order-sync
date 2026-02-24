from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Employee
from django.contrib.auth.models import User
from .forms import RegisterForm



def login_user(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid username or password"

    return render(request, "login.html", {"error": error})


@login_required(login_url="login")
def dashboard(request):
    employee = Employee.objects.get(user=request.user)
    return render(request, "dashboard.html", {"employee": employee})


def logout_user(request):
    logout(request)
    return redirect("login")

from django.shortcuts import render
from .models import Employee

