from django.db import models


class InventoryMove(models.Model):
    FROM_CHOICES = [("store", "Store"), ("website", "Website")]
    TO_CHOICES = [("store", "Store"), ("website", "Website")]
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="moves", null=True, blank=True)
    po_item = models.ForeignKey('vendors.PurchaseOrderItem', on_delete=models.CASCADE, related_name="moves", null=True, blank=True)
    from_location = models.CharField(max_length=10, choices=FROM_CHOICES)
    to_location = models.CharField(max_length=10, choices=TO_CHOICES)
    qty = models.PositiveIntegerField()
    moved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        item_ref = self.product.sku if self.product else (self.po_item.po_sku if self.po_item else "Unknown")
        return f"{item_ref} {self.from_location}->{self.to_location} qty={self.qty}"
