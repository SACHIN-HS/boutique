from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('vendor/', include('apps.vendors.urls')),
    path('product/', include('apps.products.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('orders/', include('apps.orders.urls')),
    path('tailoring/', include('apps.tailoring.urls')),
    path('accounting/', include('apps.accounting.urls')),
]
