from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import path
from .models import Attendance
from staff.models import Staff


class AttendanceAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk/', self.admin_site.admin_view(self.bulk_attendance_view), name='attendance_attendance_bulk'),
            path('history/', self.admin_site.admin_view(self.history_view), name='attendance_attendance_history'),
            path('<int:pk>/edit/', self.admin_site.admin_view(self.edit_attendance_view), name='attendance_attendance_edit'),
        ]
        return custom_urls + urls

    # ✅ Change click → History page
    def changelist_view(self, request, extra_context=None):
        return redirect('admin:attendance_attendance_history')

    # ✅ Add click → Bulk attendance page
    def add_view(self, request, form_url='', extra_context=None):
        return redirect('admin:attendance_attendance_bulk')

    # ✅ Bulk Attendance Mark
    def bulk_attendance_view(self, request):
        staff_list = Staff.objects.all()
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
            return redirect('admin:attendance_attendance_history')

        existing = {a.staff_id: a.status for a in Attendance.objects.filter(date=selected_date)}

        context = {
            **self.admin_site.each_context(request),
            "staff_list": staff_list,
            "today": selected_date,
            "existing": existing,
            "title": "Bulk Attendance",
        }
        return render(request, "admin/attendance_bulk.html", context)

    # ✅ History Page
    def history_view(self, request):
        filter_date = request.GET.get("filter_date", "")

        staff_list = Staff.objects.all()
        staff_summary = []
        for staff in staff_list:
            qs = Attendance.objects.filter(staff=staff)
            present = qs.filter(status='present').count()
            absent = qs.filter(status='absent').count()
            staff_summary.append({
                'staff': staff,
                'present': present,
                'absent': absent,
                'total': present + absent,
            })

        records = Attendance.objects.select_related('staff').order_by('-date', 'staff__name')
        if filter_date:
            records = records.filter(date=filter_date)

        context = {
            **self.admin_site.each_context(request),
            "title": "Attendance History",
            "staff_summary": staff_summary,
            "records": records,
            "filter_date": filter_date,
        }
        return render(request, "admin/attendance_history.html", context)

    # ✅ Edit Single Record
    def edit_attendance_view(self, request, pk):
        try:
            record = Attendance.objects.get(pk=pk)
        except Attendance.DoesNotExist:
            self.message_user(request, "Record not found!", messages.ERROR)
            return redirect('admin:attendance_attendance_history')

        if request.method == "POST":
            new_status = request.POST.get("status")
            if new_status in ['present', 'absent']:
                record.status = new_status
                record.save()
                self.message_user(request, f"Updated: {record.staff.name} - {record.date}", messages.SUCCESS)
            return redirect('admin:attendance_attendance_history')

        context = {
            **self.admin_site.each_context(request),
            "title": "Edit Attendance",
            "record": record,
        }
        return render(request, "admin/attendance_edit.html", context)


admin.site.register(Attendance, AttendanceAdmin)