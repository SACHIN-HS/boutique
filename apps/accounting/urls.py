from django.urls import path
from . import views

urlpatterns = [
    path('pl/', views.accounting_pl, name='accounting_pl'),
    path('expenses/', views.accounting_expenses, name='accounting_expenses'),
    path('expenses/delete/<int:pk>/', views.expense_delete, name='expense_delete'),
]
