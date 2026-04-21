from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.product_add, name='product_add'),
    path('', views.product_view, name='product_view'),
    path('edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('sku/', views.sku_center, name='sku_center'),
    path('sku/mark-printed/<int:item_pk>/', views.sku_mark_printed, name='sku_mark_printed'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('add-category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('add-size/', views.add_size, name='add_size'),
    path('add-size/edit/<int:pk>/', views.edit_size, name='edit_size'),
    path('add-size/delete/<int:pk>/', views.delete_size, name='delete_size'),
]
