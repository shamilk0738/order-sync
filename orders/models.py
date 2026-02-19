from django.db import models
from django.contrib.auth.models import User
from store.models import AdminStore
from product.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('complete', 'Complete'),
        ('cancelled', 'Cancelled'),
    ]

    order_name = models.CharField(max_length=200, blank=True)
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    store      = models.ForeignKey(AdminStore, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='orders')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_name or f"Order #{self.id}"

    def recalculate_total(self):
        self.total_price = sum(i.subtotal for i in self.items.all())
        self.save()


class OrderItem(models.Model):
    order    = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.quantity * self.product.rate

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"