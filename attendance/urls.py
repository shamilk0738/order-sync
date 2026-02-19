from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_summary, name='attendance_summary'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
]
