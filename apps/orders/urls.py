from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('send-to-tailor/<int:item_pk>/', views.order_send_to_tailor, name='order_send_to_tailor'),
]
