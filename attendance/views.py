from django.shortcuts import render, redirect
from .models import Staff, Attendance
from django.utils import timezone

def attendance(request):
    staffs = Staff.objects.all()
    today = timezone.now().date()

    if request.method == "POST":
        for staff in staffs:
            # Check if checkbox is checked
            present = request.POST.get(f'staff_{staff.id}') == 'on'
            # Update or create today's attendance
            Attendance.objects.update_or_create(
                staff=staff,
                date=today,
                defaults={'present': present}
            )
        return redirect('attendance')

    # Get today's attendance if exists
    attendance_records = Attendance.objects.filter(date=today)
    attendance_dict = {a.staff.id: a.present for a in attendance_records}

    return render(request, "attendance/attendance.html", {
        "staffs": staffs,
        "attendance_dict": attendance_dict,
        "today": today
    })
