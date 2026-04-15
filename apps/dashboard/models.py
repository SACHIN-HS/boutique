from django.db import models


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    CATEGORY_CHOICES = [
        ("Men", "Men"),
        ("Women", "Women"),
        ("Kids", "Kids"),
        ("Jewelry", "Jewelry"),
    ]
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    qty = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    sizes = models.CharField(max_length=200, blank=True)
    colors = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_tags = models.CharField(max_length=300, blank=True)
    meta_description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Verified", "Verified"),
    ]
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(
        Vendor, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.po_number


class POItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    qty = models.PositiveIntegerField(default=0)
    colors = models.CharField(max_length=200, blank=True)
    sizes = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    received = models.BooleanField(default=False)
    sku_printed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.name}"


class InventoryMove(models.Model):
    FROM_CHOICES = [("store", "Store"), ("website", "Website")]
    TO_CHOICES = [("store", "Store"), ("website", "Website")]
    po_item = models.ForeignKey(POItem, on_delete=models.CASCADE, related_name="moves")
    from_location = models.CharField(max_length=10, choices=FROM_CHOICES)
    to_location = models.CharField(max_length=10, choices=TO_CHOICES)
    qty = models.PositiveIntegerField()
    moved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.po_item} {self.from_location}->{self.to_location} qty={self.qty}"


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
        OrderItem, on_delete=models.CASCADE, related_name="tailoring_jobs"
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


class Expense(models.Model):
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"
