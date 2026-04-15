from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.product_add_view, name='product_add'),
    path('view/', views.product_view, name='product_view'),
    # Note: 'sku/' is handled at the root level if needed, 
    # but here we can keep it as is if we include correctly.
]
