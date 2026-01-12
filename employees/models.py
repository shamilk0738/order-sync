from django.db import models
from django.contrib.auth.models import User

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    emp_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    join_date = models.DateField()
    attendance_percentage = models.FloatField()

    def __str__(self):
        return self.user.username
