from django.urls import path
from . import views

urlpatterns = [
    path('pnl/', views.accounting_pnl_view, name='accounting_pnl'),
    path('expenses/', views.accounting_expenses_view, name='accounting_expenses'),
]
