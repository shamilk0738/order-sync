from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_name = models.CharField(
        max_length=100,
        help_text="Group name of the order",
        default=""
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_name} - {self.user.username}"

    def total_price(self):
        total = sum(item.product.rate * item.quantity for item in self.items.all())
        return total
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def subtotal(self):
        return self.product.rate * self.quantity
