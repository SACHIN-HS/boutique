from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.vendor_add, name='vendor_add'),
    path('', views.vendor_view, name='vendor_view'),
    path('edit/<int:pk>/', views.vendor_edit, name='vendor_edit'),
    path('delete/<int:pk>/', views.vendor_delete, name='vendor_delete'),
    path('po/', views.po_list, name='po_list'),
    path('po/create/', views.po_create, name='po_create'),
    path('po/receive/<int:pk>/', views.po_receive, name='po_receive'),
    
    # Vendor Portal
    path('portal/<str:token>/', views.portal_login, name='portal_login'),
    path('portal/dashboard/<str:token>/', views.portal_dashboard, name='portal_dashboard'),
    path('portal/history/<str:token>/', views.portal_history, name='portal_history'),
    path('portal/logout/<str:token>/', views.portal_logout, name='portal_logout'),
    path('portal/po/qr/<str:token>/<str:po_number>/', views.portal_po_qr, name='portal_po_qr'),
    path('portal/po/items/<str:token>/<str:po_number>/', views.portal_po_items, name='portal_po_items'),
]
