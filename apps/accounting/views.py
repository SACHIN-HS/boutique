from django.shortcuts import render


def accounting_pnl_view(request):
    context = {
        'revenue': 400.99,
        'cost': 590.00,
        'expenses': 0.00,
        'net_profit': -189.01,
        'entries': mock_db.ACCOUNTING_ENTRIES
    }
    return render(request, 'accounting/accounting_pnl.html', context)

def accounting_expenses_view(request):
    return render(request, 'accounting/accounting_expenses.html')
