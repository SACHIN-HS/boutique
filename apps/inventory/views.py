from django.shortcuts import render


def inventory_view(request):
    context = {
        'store_inventory': mock_db.INVENTORY_STORE,
        'website_inventory': mock_db.INVENTORY_WEBSITE
    }
    return render(request, 'inventory/inventory.html', context)
