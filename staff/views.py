from django.shortcuts import render, redirect
from .models import Staff

def staff_index(request):   # 👈 പേര് മാറ്റി
    if request.method == "POST":
        Staff.objects.create(
            name=request.POST['name'],
            position=request.POST['position'],
            phone=request.POST['phone'],
            route=request.POST['route'],
            photo=request.FILES.get('photo')  # safer
        )
        return redirect('staff_index')

    staffs = Staff.objects.all()
    return render(request, 'staff/staff_list.html', {'staffs': staffs})
