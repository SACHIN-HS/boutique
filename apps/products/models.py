from django.db import models


class VariantCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VariantSize(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VariantColor(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VariantStyle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class VariantGender(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    style = models.ForeignKey(
        "VariantStyle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    gender = models.ForeignKey(
        "VariantGender",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    qty = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    reseller_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sizes = models.CharField(max_length=200, blank=True)
    colors = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_tags = models.CharField(max_length=300, blank=True)
    meta_description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    qty = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.color}/{self.size} ({self.qty})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product_id}"
