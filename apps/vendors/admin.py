from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, PurchaseOrderVerification

admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderVerification)


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "purchase_order",
        "item_code",
        "po_sku",
        "reseller_price",
        "reseller_sku",
        "qty",
        "unit_price",
        "status",
    )
    list_select_related = ("purchase_order",)
    search_fields = ("item_code", "po_sku", "reseller_sku", "purchase_order__po_number")
