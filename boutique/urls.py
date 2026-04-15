"""
URL configuration for boutique project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from apps.products import views as product_views
from apps.orders import views as order_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('vendor/', include('apps.vendors.urls')),
    path('product/', include('apps.products.urls')),
    path('sku/', product_views.sku_view, name='sku'),
    path('inventory/', include('apps.inventory.urls')),
    path('order/', include('apps.orders.urls')),
    path('po-order/', order_views.po_order_view, name='po_order'),
    path('tailoring/', include('apps.tailoring.urls')),
    path('accounting/', include('apps.accounting.urls')),
]
