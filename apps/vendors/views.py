from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from .models import Vendor, PurchaseOrder, POItem


@login_required(login_url='login')
def vendor_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        if name and email and phone and address:
            Vendor.objects.create(name=name, email=email, phone=phone, address=address)
            messages.success(request, 'Vendor saved successfully!')
            return redirect('vendor_view')
        messages.error(request, 'Please fill all fields.')
    return render(request, 'vendors/vendor_add.html')


@login_required(login_url='login')
def vendor_view(request):
    vendors = Vendor.objects.order_by('-created_at')
    return render(request, 'vendors/vendor_view.html', {'vendors': vendors})


@login_required(login_url='login')
def vendor_delete(request, pk):
    get_object_or_404(Vendor, pk=pk).delete()
    messages.success(request, 'Vendor deleted.')
    return redirect('vendor_view')


@login_required(login_url='login')
def po_list(request):
    pos = PurchaseOrder.objects.select_related('vendor').prefetch_related('items').order_by('-created_at')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')
    if date_from:
        pos = pos.filter(created_at__date__gte=date_from)
    if date_to:
        pos = pos.filter(created_at__date__lte=date_to)
    total_value = pos.aggregate(t=Sum('total'))['t'] or 0
    return render(request, 'orders/po_list.html', {
        'pos': pos, 'total_value': total_value,
        'date_from': date_from, 'date_to': date_to,
    })


@login_required(login_url='login')
def po_create(request):
    vendors = Vendor.objects.order_by('name')
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        po_number = f"PO-{int(timezone.now().timestamp())}"
        po = PurchaseOrder.objects.create(vendor=vendor, po_number=po_number)

        names = request.POST.getlist('item_name')
        categories = request.POST.getlist('item_category')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        colors_list = request.POST.getlist('item_colors')
        sizes_list = request.POST.getlist('item_sizes')

        total = 0
        for i, name in enumerate(names):
            if not name.strip():
                continue
            qty = int(qtys[i] or 0)
            price = float(prices[i] or 0)
            line_total = qty * price
            total += line_total
            POItem.objects.create(
                purchase_order=po, name=name.strip(),
                category=categories[i] if i < len(categories) else '',
                qty=qty, price=price, line_total=line_total,
                colors=colors_list[i] if i < len(colors_list) else '',
                sizes=sizes_list[i] if i < len(sizes_list) else '',
            )
        po.total = total
        po.save()
        messages.success(request, f'Purchase Order {po_number} created!')
        return redirect('po_list')
    return render(request, 'vendors/po_create.html', {'vendors': vendors})


@login_required(login_url='login')
def po_receive(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        received_ids = request.POST.getlist('received')
        po.items.all().update(received=False)
        if received_ids:
            po.items.filter(pk__in=received_ids).update(received=True)
        total = po.items.count()
        received_count = po.items.filter(received=True).count()
        if received_count == 0:
            po.status = 'Pending'
        elif received_count < total:
            po.status = 'Partial'
        else:
            po.status = 'Verified'
        po.save()
        messages.success(request, 'PO receipt updated!')
        return redirect('po_list')
    return render(request, 'vendors/po_receive.html', {'po': po})
