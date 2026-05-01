from django.contrib import admin
from .models import Product, ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "style", "gender", "sku", "qty", "reseller_price")
    search_fields = ("name", "sku", "category")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image", "created_at")
