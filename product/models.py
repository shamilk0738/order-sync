import uuid
from django.db import models

class Product(models.Model):
    product_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    stock = models.IntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name

    def is_available(self, qty=1):
        return self.stock >= qty
