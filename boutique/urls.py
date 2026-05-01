from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('vendors/', include('apps.vendors.urls')),
    path('vendor/', include('apps.vendors.urls')),
    path('product/', include('apps.products.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('orders/', include('apps.orders.urls')),
    path('tailoring/', include('apps.tailoring.urls')),
    path('accounting/', include('apps.accounting.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
