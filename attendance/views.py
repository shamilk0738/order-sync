from django.shortcuts import render, redirect
from django.utils import timezone
from staff.models import Staff
from .models import Attendance


# ✅ Summary Page
def attendance_summary(request):
    today = timezone.localdate()

    staff_list = Staff.objects.all().order_by('name')
    summary = []

    for staff in staff_list:
        present_count = Attendance.objects.filter(
            staff=staff, status='present'
        ).count()

        absent_count = Attendance.objects.filter(
            staff=staff, status='absent'
        ).count()

        today_record = Attendance.objects.filter(
            staff=staff, date=today
        ).first()

        today_status = today_record.status if today_record else "not marked"

        total_attendance = present_count + absent_count

        summary.append({
            'staff': staff,
            'present': present_count,
            'absent': absent_count,
            'total': total_attendance,
            'today': today_status
        })

    return render(request, "attendance/summary.html", {
        'summary': summary,
        'today': today
    })


# ✅ Mark Attendance (Today മാത്രം)
def mark_attendance(request):
    today = timezone.localdate()
    staff_list = Staff.objects.all()

    if request.method == "POST":
        for staff in staff_list:
            status = request.POST.get(f"staff_{staff.id}")

            if status:
                Attendance.objects.update_or_create(
                    staff=staff,
                    date=today,
                    defaults={'status': status}
                )

        return redirect('attendance_summary')  # after save

    return render(request, "attendance/summary.html", {
        'staff_list': staff_list,
        'today': today
    })
