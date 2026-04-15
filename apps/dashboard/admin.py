from django.contrib import admin
from .models import (
    Vendor,
    Product,
    PurchaseOrder,
    POItem,
    InventoryMove,
    Order,
    OrderItem,
    Tailor,
    TailoringJob,
    Expense,
)

admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(PurchaseOrder)
admin.site.register(POItem)
admin.site.register(InventoryMove)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Tailor)
admin.site.register(TailoringJob)
admin.site.register(Expense)
