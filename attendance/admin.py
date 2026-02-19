from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Attendance
from staff.models import Staff


class AttendanceAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context=None):
        staff_list = Staff.objects.all()

        # Default date = today
        selected_date = request.POST.get("attendance_date") or request.GET.get("attendance_date")
        if not selected_date:
            selected_date = timezone.localdate()

        if request.method == "POST":

            for staff in staff_list:
                status = request.POST.get(f"staff_{staff.id}")

                if status:
                    Attendance.objects.update_or_create(
                        staff=staff,
                        date=selected_date,
                        defaults={"status": status}
                    )

            self.message_user(request, "Attendance saved successfully!", messages.SUCCESS)

            return redirect(request.path)

        context = {
            "staff_list": staff_list,
            "today": selected_date,
        }

        return render(request, "admin/attendance_bulk.html", context)


admin.site.register(Attendance, AttendanceAdmin)