from django.db import models


class InventoryMove(models.Model):
    FROM_CHOICES = [("store", "Store"), ("website", "Website")]
    TO_CHOICES = [("store", "Store"), ("website", "Website")]
    po_item = models.ForeignKey('vendors.POItem', on_delete=models.CASCADE, related_name="moves")
    from_location = models.CharField(max_length=10, choices=FROM_CHOICES)
    to_location = models.CharField(max_length=10, choices=TO_CHOICES)
    qty = models.PositiveIntegerField()
    moved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.po_item} {self.from_location}->{self.to_location} qty={self.qty}"
