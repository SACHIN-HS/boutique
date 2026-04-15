from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from apps.vendors.models import PurchaseOrderItem
from .models import InventoryMove


@login_required(login_url='login')
def inventory(request):
    printed_items = PurchaseOrderItem.objects.filter(
        sku_printed=True, purchase_order__status='Verified'
    ).select_related('purchase_order__vendor')

    store_items = []
    website_items = []
    for item in printed_items:
        to_website = item.moves.filter(from_location='store', to_location='website').aggregate(t=Sum('qty'))['t'] or 0
        to_store = item.moves.filter(from_location='website', to_location='store').aggregate(t=Sum('qty'))['t'] or 0
        store_qty = item.qty - to_website + to_store
        website_qty = to_website - to_store
        if store_qty > 0:
            store_items.append({'item': item, 'qty': store_qty})
        if website_qty > 0:
            website_items.append({'item': item, 'qty': website_qty})

    if request.method == 'POST':
        item_pk = request.POST.get('item_pk')
        direction = request.POST.get('direction')
        qty = int(request.POST.get('qty', 0) or 0)
        if item_pk and direction and qty > 0:
            item = get_object_or_404(PurchaseOrderItem, pk=item_pk)
            if direction == 'to_website':
                InventoryMove.objects.create(po_item=item, from_location='store', to_location='website', qty=qty)
            elif direction == 'to_store':
                InventoryMove.objects.create(po_item=item, from_location='website', to_location='store', qty=qty)
            messages.success(request, 'Stock moved successfully!')
            return redirect('inventory')

    return render(request, 'inventory/inventory.html', {
        'store_items': store_items,
        'website_items': website_items,
    })
