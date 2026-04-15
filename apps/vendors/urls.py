from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.vendor_add_view, name='vendor_add'),
    path('view/', views.vendor_view, name='vendor_view'),
]
