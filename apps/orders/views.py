from django.shortcuts import render

def order_view(request):
    context = {'orders': mock_db.ORDERS}
    return render(request, 'orders/order.html', context)

def po_order_view(request):
    context = {
        'po_orders': mock_db.PO_ORDERS,
        'stock_summary': mock_db.INVENTORY_STORE
    }
    return render(request, 'orders/po_order.html', context)

def po(request):
    return render(request, 'orders/po.html')