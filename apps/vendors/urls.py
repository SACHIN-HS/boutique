from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.vendor_add, name='vendor_add'),
    path('', views.vendor_view, name='vendor_view'),
    path('delete/<int:pk>/', views.vendor_delete, name='vendor_delete'),
    path('po/', views.po_list, name='po_list'),
    path('po/create/', views.po_create, name='po_create'),
    path('po/receive/<int:pk>/', views.po_receive, name='po_receive'),
]
