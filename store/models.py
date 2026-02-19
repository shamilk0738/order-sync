from django.db import models

class AdminStore(models.Model):
    store_name = models.CharField(max_length=200)
    gst_number = models.CharField(max_length=20)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    alternate_number = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.store_name