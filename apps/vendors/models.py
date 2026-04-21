from django.db import models
import uuid

class Vendor(models.Model):
    portal_token = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Submitted", "Submitted"),
        ("Received", "Received"),
        ("Verified", "Verified"),
        ("Rejected", "Rejected"),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="purchase_orders")
    po_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.po_number


class PurchaseOrderItem(models.Model):
    ITEM_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Verified", "Verified"),
        ("Defective", "Defective"),
    ]
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    qty = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ITEM_STATUS_CHOICES, default="Pending")
    
    # Legacy fields for inventory/dashboard tracking
    received = models.BooleanField(default=False)
    sku_printed = models.BooleanField(default=False)

    @property
    def name(self):
        return self.item_name

    def __str__(self):
        return f"{self.item_name} ({self.color}/{self.size})"


class PurchaseOrderVerification(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="verifications")
    status = models.CharField(max_length=20, choices=PurchaseOrder.STATUS_CHOICES)
    admin_notes = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=100) # Admin identifier

    def __str__(self):
        return f"Verification for {self.po.po_number} - {self.status}"
