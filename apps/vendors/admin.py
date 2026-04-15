from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, PurchaseOrderVerification

admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderItem)
admin.site.register(PurchaseOrderVerification)
