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
    gender = models.CharField(
        max_length=10,
        choices=[("Men", "Men"), ("Women", "Women"), ("Kids", "Kids")],
        blank=True,
        default="",
    )
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
    variant_style = models.ForeignKey(
        "products.VariantStyle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",
    )
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
    item_code = models.CharField(max_length=100, blank=True)
    po_sku = models.CharField(max_length=64, blank=True)
    reseller_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reseller_sku = models.CharField(max_length=64, blank=True)
    category = models.CharField(max_length=100, blank=True)
    variant_style = models.ForeignKey(
        "products.VariantStyle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_order_items",
    )
    variant_gender = models.ForeignKey(
        "products.VariantGender",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_order_items",
    )
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
        return self.item_code or self.category or "Item"

    def __str__(self):
        base = self.item_code or self.category or "Item"
        return f"{base} ({self.color}/{self.size})"


class PurchaseOrderVerification(models.Model):
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="verifications")
    status = models.CharField(max_length=20, choices=PurchaseOrder.STATUS_CHOICES)
    admin_notes = models.TextField(blank=True, null=True)
    verified_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.CharField(max_length=100) # Admin identifier

    def __str__(self):
        return f"Verification for {self.po.po_number} - {self.status}"
