from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_view, name='order'),
    path('po/', views.po_order_view, name='po_order'),
    path('po1/', views.po, name='po'),
]
