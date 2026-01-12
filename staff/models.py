from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    supply_route = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)

    def __str__(self):
        return self.name
