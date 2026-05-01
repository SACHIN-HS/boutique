from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from apps.vendors.models import PurchaseOrderItem
from apps.products.models import Product
from .models import InventoryMove


@login_required(login_url='login')
def inventory(request):
    from django.db.models import Q

    # Annotate products with their total moves in one go
    products_qs = Product.objects.annotate(
        total_to_website=Sum("moves__qty", filter=Q(moves__from_location="store", moves__to_location="website")),
        total_to_store=Sum("moves__qty", filter=Q(moves__from_location="website", moves__to_location="store")),
    ).order_by("-updated_at")

    # Map products to their PO info for display (still using a map for efficiency)
    po_items_map = {}
    po_items_qs = (
        PurchaseOrderItem.objects.filter(purchase_order__status="Verified")
        .exclude(po_sku="")
        .select_related("purchase_order__vendor")
        .order_by("-id")
    )
    for p_item in po_items_qs:
        if p_item.po_sku not in po_items_map:
            po_items_map[p_item.po_sku] = p_item

    store_items = []
    website_items = []

    for product in products_qs:
        to_website = product.total_to_website or 0
        to_store = product.total_to_store or 0
        
        website_qty = to_website - to_store
        store_qty = product.qty - website_qty

        item_data = {
            "product": product,
            "po_item": po_items_map.get(product.sku),
        }

        if store_qty > 0:
            store_items.append({**item_data, "qty": store_qty})
        if website_qty > 0:
            website_items.append({**item_data, "qty": website_qty})

    if request.method == "POST":
        product_pk = request.POST.get("product_pk")
        direction = request.POST.get("direction")
        qty = int(request.POST.get("qty", 0) or 0)
        if product_pk and direction and qty > 0:
            product = get_object_or_404(Product, pk=product_pk)
            if direction == "to_website":
                InventoryMove.objects.create(
                    product=product, from_location="store", to_location="website", qty=qty
                )
            elif direction == "to_store":
                InventoryMove.objects.create(
                    product=product, from_location="website", to_location="store", qty=qty
                )
            messages.success(request, 'Stock moved successfully!')
            return redirect('inventory')

    return render(request, 'inventory/inventory.html', {
        'store_items': store_items,
        'website_items': website_items,
    })
