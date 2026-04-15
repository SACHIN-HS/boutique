from django.contrib import admin
from .models import Vendor, PurchaseOrder, POItem

admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(POItem)
