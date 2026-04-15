from django.shortcuts import render

def product_add_view(request):
    return render(request, 'products/product_add.html')

def product_view(request):
    context = {'products': mock_db.PRODUCTS}
    return render(request, 'products/product_view.html', context)

def sku_view(request):
    context = {
        'po_orders': mock_db.PO_ORDERS,
        'verified_items': [
            {"po": "PO-SKU-2001", "vendor": "Delhi Boutique Supply", "item": "Kurti - Floral Print", "category": "Women", "verified": True, "colors": "Red, Blue", "sizes": "M, L", "qty": 18, "price": 12.50, "printed": True}
        ]
    }
    return render(request, 'products/sku.html', context)
