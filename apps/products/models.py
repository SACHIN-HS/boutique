from django.db import models


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
