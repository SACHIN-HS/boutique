from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, PurchaseOrderVerification
from apps.products.models import VariantCategory, VariantSize


# --- Admin Views ---

@login_required(login_url='login')
def vendor_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()
        
        if name and email and address and password:
            vendor = Vendor.objects.create(
                name=name, email=email, phone=phone, 
                address=address, password_hash=make_password(password)
            )
            messages.success(request, f'Vendor {name} created successfully!')
            return redirect('vendor_view')
        messages.error(request, 'Please fill all mandatory fields.')
    return render(request, 'vendors/vendor_add.html')


@login_required(login_url='login')
def vendor_view(request):
    vendors = Vendor.objects.order_by('-created_at')
    # Pre-calculating portal links for convenience
    host = request.get_host()
    for v in vendors:
        v.portal_url = f"http://{host}/vendors/portal/{v.portal_token}/"
    return render(request, 'vendors/vendor_view.html', {'vendors': vendors})


@login_required(login_url='login')
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        vendor.name = request.POST.get('name', '').strip()
        vendor.email = request.POST.get('email', '').strip()
        vendor.phone = request.POST.get('phone', '').strip()
        vendor.address = request.POST.get('address', '').strip()
        vendor.is_active = request.POST.get('is_active') == 'on'
        
        password = request.POST.get('password', '').strip()
        if password:
            vendor.password_hash = make_password(password)
            
        vendor.save()
        messages.success(request, f'Vendor {vendor.name} updated successfully!')
        return redirect('vendor_view')
    return render(request, 'vendors/vendor_edit.html', {'vendor': vendor})


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
    selected_po = None
    selected_po_id = request.GET.get('po', '')
    if date_from:
        pos = pos.filter(created_at__date__gte=date_from)
    if date_to:
        pos = pos.filter(created_at__date__lte=date_to)

    if selected_po_id:
        try:
            selected_po = pos.filter(id=int(selected_po_id)).first()
        except (TypeError, ValueError):
            selected_po = None
    
    total_value = pos.aggregate(t=Sum('grand_total'))['t'] or 0
    stock_summary = (
        PurchaseOrderItem.objects
        .filter(purchase_order__in=pos)
        .values('item_name', 'category', 'color', 'size')
        .annotate(total_qty=Sum('qty'), total_value=Sum('total_value'))
        .order_by('item_name', 'category', 'color', 'size')
    )
    return render(request, 'orders/po_list.html', {
        'pos': pos, 'total_value': total_value,
        'stock_summary': stock_summary,
        'date_from': date_from, 'date_to': date_to,
        'selected_po': selected_po,
    })



@login_required(login_url='login')
def po_create(request):
    # This remains as an admin-side manual PO creation tool if needed
    vendors = Vendor.objects.filter(is_active=True).order_by('name')
    if request.method == 'POST':
        vendor_id = request.POST.get('vendor')
        vendor = get_object_or_404(Vendor, pk=vendor_id)
        po_number = f"PO-{int(timezone.now().timestamp())}"
        po = PurchaseOrder.objects.create(vendor=vendor, po_number=po_number, status="Submitted")

        names = request.POST.getlist('item_name')
        categories = request.POST.getlist('item_category')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        colors = request.POST.getlist('item_color')
        sizes = request.POST.getlist('item_size')

        grand_total = 0
        for i, name in enumerate(names):
            if not name.strip():
                continue
            qty = int(qtys[i] or 0)
            price = float(prices[i] or 0)
            total_val = qty * price
            grand_total += total_val
            PurchaseOrderItem.objects.create(
                purchase_order=po, item_name=name.strip(),
                category=categories[i] if i < len(categories) else '',
                qty=qty, unit_price=price, total_value=total_val,
                color=colors[i] if i < len(colors) else '',
                size=sizes[i] if i < len(sizes) else '',
            )
        po.grand_total = grand_total
        po.save()
        messages.success(request, f'Purchase Order {po_number} created!')
        return redirect('po_list')
    return render(request, 'vendors/po_create.html', {
        'vendors': vendors,
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'sizes': VariantSize.objects.values_list('name', flat=True),
    })


@login_required(login_url='login')
def po_receive(request, pk):
    # This could be adapted for the verification step
    po = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('admin_notes', '')
        po.status = status
        po.remarks = notes
        po.save()
        
        PurchaseOrderVerification.objects.create(
            po=po, status=status, admin_notes=notes, 
            verified_by=request.user.username
        )
        
        messages.success(request, f'PO {po.po_number} status updated to {status}!')
        return redirect('po_list')
    return render(request, 'vendors/po_receive.html', {'po': po})


# --- Vendor Portal Views ---

def portal_login(request, token):
    vendor = get_object_or_404(Vendor, portal_token=token, is_active=True)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email == vendor.email and check_password(password, vendor.password_hash):
            request.session['vendor_id'] = vendor.id
            return redirect('portal_dashboard', token=token)
        messages.error(request, "Invalid email or password.")
    return render(request, 'vendors/portal_login.html', {'vendor': vendor})

def check_vendor_session(request, token):
    vendor_id = request.session.get('vendor_id')
    if not vendor_id:
        return None
    vendor = Vendor.objects.filter(id=vendor_id, portal_token=token, is_active=True).first()
    return vendor

def portal_dashboard(request, token):
    vendor = check_vendor_session(request, token)
    if not vendor:
        return redirect('portal_login', token=token)
    
    if request.method == 'POST':
        po_number = f"PO-{vendor.id}-{int(timezone.now().timestamp())}"
        po = PurchaseOrder.objects.create(vendor=vendor, po_number=po_number, status="Submitted")
        
        names = request.POST.getlist('item_name')
        categories = request.POST.getlist('item_category')
        colors = request.POST.getlist('item_color')
        sizes = request.POST.getlist('item_size')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        
        grand_total = 0
        for i, name in enumerate(names):
            if not name.strip(): continue
            qty = int(qtys[i] or 0)
            price = float(prices[i] or 0)
            total_val = qty * price
            grand_total += total_val
            
            PurchaseOrderItem.objects.create(
                purchase_order=po, item_name=name, category=categories[i],
                color=colors[i], size=sizes[i], qty=qty, unit_price=price,
                total_value=total_val
            )
        po.grand_total = grand_total
        po.save()
        messages.success(request, f"Purchase Order {po_number} submitted successfully!")
        return redirect('portal_history', token=token)
        
    return render(request, 'vendors/portal_dashboard.html', {
        'vendor': vendor,
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'sizes': VariantSize.objects.values_list('name', flat=True),
    })

def portal_history(request, token):
    vendor = check_vendor_session(request, token)
    if not vendor:
        return redirect('portal_login', token=token)
    
    pos = PurchaseOrder.objects.filter(vendor=vendor).prefetch_related('items').order_by('-created_at')
    return render(request, 'vendors/portal_history.html', {'vendor': vendor, 'pos': pos})

def portal_logout(request, token):
    if 'vendor_id' in request.session:
        del request.session['vendor_id']
    return redirect('portal_login', token=token)

