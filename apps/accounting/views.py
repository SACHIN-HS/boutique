from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F

from .models import Expense
from apps.orders.models import OrderItem
from apps.vendors.models import POItem


@login_required(login_url='login')
def accounting_pl(request):
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    orders_qs = OrderItem.objects.select_related('order')
    pos_qs = POItem.objects.select_related('purchase_order')
    expenses_qs = Expense.objects.all()

    if date_from:
        orders_qs = orders_qs.filter(order__created_at__date__gte=date_from)
        pos_qs = pos_qs.filter(purchase_order__created_at__date__gte=date_from)
        expenses_qs = expenses_qs.filter(date__gte=date_from)
    if date_to:
        orders_qs = orders_qs.filter(order__created_at__date__lte=date_to)
        pos_qs = pos_qs.filter(purchase_order__created_at__date__lte=date_to)
        expenses_qs = expenses_qs.filter(date__lte=date_to)

    sales_revenue = orders_qs.aggregate(t=Sum(F('price') * F('qty')))['t'] or 0
    purchases_total = pos_qs.aggregate(t=Sum(F('price') * F('qty')))['t'] or 0
    expenses_total = expenses_qs.aggregate(t=Sum('amount'))['t'] or 0
    gross_profit = sales_revenue - purchases_total
    net_profit = gross_profit - expenses_total

    return render(request, 'accounting/accounting_pl.html', {
        'sales_revenue': sales_revenue,
        'purchases_total': purchases_total,
        'expenses_total': expenses_total,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'sales_lines': orders_qs,
        'purchase_lines': pos_qs,
        'expense_lines': expenses_qs,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required(login_url='login')
def accounting_expenses(request):
    if request.method == 'POST':
        category = request.POST.get('category', '').strip()
        amount = request.POST.get('amount', '').strip()
        date = request.POST.get('date', '').strip()
        note = request.POST.get('note', '').strip()
        if category and amount and date:
            Expense.objects.create(category=category, amount=amount, date=date, note=note)
            messages.success(request, 'Expense saved!')
            return redirect('accounting_expenses')
        messages.error(request, 'Please fill required fields.')

    expenses = Expense.objects.order_by('-date')
    return render(request, 'accounting/accounting_expenses.html', {'expenses': expenses})


@login_required(login_url='login')
def expense_delete(request, pk):
    get_object_or_404(Expense, pk=pk).delete()
    messages.success(request, 'Expense deleted.')
    return redirect('accounting_expenses')
