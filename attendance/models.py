from django.db import models

# Create your models here.
from django.db import models

# Staff model
class Staff(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Attendance model
class Attendance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.staff.name} - {self.date} - {'Present' if self.present else 'Absent'}"
