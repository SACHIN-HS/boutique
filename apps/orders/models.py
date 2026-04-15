from django.db import models


class Order(models.Model):
    order_no = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_no


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ("Sold", "Sold"),
        ("Sent to tailoring", "Sent to tailoring"),
        ("Stitching done", "Stitching done"),
        ("Delivered", "Delivered"),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    qty = models.PositiveIntegerField(default=1)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Sold")

    def __str__(self):
        return f"{self.order.order_no} - {self.name}"
