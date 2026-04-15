from django.db import models


class Tailor(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TailoringJob(models.Model):
    STATUS_CHOICES = [
        ("Assigned", "Assigned"),
        ("Done", "Done"),
        ("Delivered", "Delivered"),
    ]
    job_no = models.CharField(max_length=50, unique=True)
    order_item = models.ForeignKey(
        'orders.OrderItem', on_delete=models.CASCADE, related_name="tailoring_jobs"
    )
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE, related_name="jobs")
    qty = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Assigned")
    expected_at = models.DateField(null=True, blank=True)
    expected_time = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    done_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.job_no
