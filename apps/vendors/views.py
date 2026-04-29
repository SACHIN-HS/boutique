from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, PurchaseOrderVerification
from apps.products.models import VariantCategory, VariantSize, VariantStyle, VariantGender
import uuid


# --- Admin Views ---

def _po_number_from_id(po_id: int) -> str:
    # 4-digit format (keeps growing beyond 9999 if needed)
    return f"PO-{po_id:04d}"

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
        .values('item_code', 'category', 'color', 'size')
        .annotate(total_qty=Sum('qty'), total_value=Sum('total_value'))
        .order_by('item_code', 'category', 'color', 'size')
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
        tmp_po_number = f"TMP-{uuid.uuid4().hex[:12]}"
        po = PurchaseOrder.objects.create(vendor=vendor, po_number=tmp_po_number, status="Submitted")
        po.po_number = _po_number_from_id(po.id)
        po.save(update_fields=["po_number"])

        codes = request.POST.getlist('item_code')
        categories = request.POST.getlist('item_category')
        styles = request.POST.getlist('item_style')
        genders = request.POST.getlist('item_gender')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        colors = request.POST.getlist('item_color')
        sizes = request.POST.getlist('item_size')

        grand_total = 0
        for i in range(max(len(codes), len(categories), len(styles), len(genders), len(qtys), len(prices), len(colors), len(sizes))):
            qty = int(qtys[i] or 0)
            price = float(prices[i] or 0)
            code_val = (codes[i].strip() if i < len(codes) and (codes[i] or '').strip() else '')
            cat_val = (categories[i] if i < len(categories) else '')
            style_val = (styles[i] if i < len(styles) else '')
            gender_val = (genders[i] if i < len(genders) else '')
            color_val = (colors[i] if i < len(colors) else '')
            size_val = (sizes[i] if i < len(sizes) else '')

            # Skip completely empty rows
            if not any([code_val, cat_val, style_val, gender_val, color_val, size_val]) and qty <= 0 and price <= 0:
                continue

            total_val = qty * price
            grand_total += total_val
            style_obj = None
            gender_obj = None
            try:
                style_id = style_val
                if style_id:
                    style_obj = VariantStyle.objects.filter(pk=int(style_id)).first()
            except (TypeError, ValueError):
                style_obj = None
            try:
                gender_id = gender_val
                if gender_id:
                    gender_obj = VariantGender.objects.filter(pk=int(gender_id)).first()
            except (TypeError, ValueError):
                gender_obj = None
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                item_code=code_val,
                category=cat_val,
                qty=qty, unit_price=price, total_value=total_val,
                color=color_val,
                size=size_val,
                variant_style=style_obj,
                variant_gender=gender_obj,
            )
        po.grand_total = grand_total
        po.save()
        messages.success(request, f'Purchase Order {po.po_number} created!')
        return redirect('po_list')
    return render(request, 'vendors/po_create.html', {
        'vendors': vendors,
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'sizes': VariantSize.objects.values_list('name', flat=True),
        'styles': VariantStyle.objects.all(),
        'genders': VariantGender.objects.all(),
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

from django.views.decorators.cache import never_cache

@never_cache
def portal_dashboard(request, token):
    vendor = check_vendor_session(request, token)
    if not vendor:
        return redirect('portal_login', token=token)
    
    if request.method == 'POST':
        tmp_po_number = f"TMP-{uuid.uuid4().hex[:12]}"
        po = PurchaseOrder.objects.create(vendor=vendor, po_number=tmp_po_number, status="Submitted")
        po.po_number = _po_number_from_id(po.id)
        po.save(update_fields=["po_number"])
        
        codes = request.POST.getlist('item_code')
        categories = request.POST.getlist('item_category')
        styles = request.POST.getlist('item_style')
        genders = request.POST.getlist('item_gender')
        colors = request.POST.getlist('item_color')
        sizes = request.POST.getlist('item_size')
        qtys = request.POST.getlist('item_qty')
        prices = request.POST.getlist('item_price')
        
        grand_total = 0
        for i in range(max(len(codes), len(categories), len(styles), len(genders), len(qtys), len(prices), len(colors), len(sizes))):
            qty = int(qtys[i] or 0)
            price = float(prices[i] or 0)
            code_val = (codes[i].strip() if i < len(codes) and (codes[i] or '').strip() else '')
            cat_val = (categories[i] if i < len(categories) else '')
            style_val = (styles[i] if i < len(styles) else '')
            gender_val = (genders[i] if i < len(genders) else '')
            color_val = (colors[i] if i < len(colors) else '')
            size_val = (sizes[i] if i < len(sizes) else '')

            if not any([code_val, cat_val, style_val, gender_val, color_val, size_val]) and qty <= 0 and price <= 0:
                continue

            # Server-side validation for required fields
            if not code_val or not size_val:
                messages.error(request, "Item Code and Size are required for all items.")
                # We could potentially return here, but for simplicity in this flow, 
                # we'll just skip the invalid row or we can abort the whole PO.
                # Aborting is safer.
                po.delete()
                return redirect('portal_dashboard', token=token)

            total_val = qty * price
            grand_total += total_val

            style_obj = None
            gender_obj = None
            try:
                style_id = style_val
                if style_id:
                    style_obj = VariantStyle.objects.filter(pk=int(style_id)).first()
            except (TypeError, ValueError):
                style_obj = None
            try:
                gender_id = gender_val
                if gender_id:
                    gender_obj = VariantGender.objects.filter(pk=int(gender_id)).first()
            except (TypeError, ValueError):
                gender_obj = None
            
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                category=cat_val,
                item_code=code_val,
                color=color_val,
                size=size_val,
                qty=qty,
                unit_price=price,
                total_value=total_val,
                variant_style=style_obj,
                variant_gender=gender_obj,
            )
        po.grand_total = grand_total
        po.save()
        messages.success(request, f"Purchase Order {po.po_number} submitted successfully!")
        return redirect('portal_po_qr', token=token, po_number=po.po_number)
        
    return render(request, 'vendors/portal_dashboard.html', {
        'vendor': vendor,
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'sizes': VariantSize.objects.values_list('name', flat=True),
        'styles': VariantStyle.objects.all(),
        'genders': VariantGender.objects.all(),
    })

def portal_history(request, token):
    vendor = check_vendor_session(request, token)
    if not vendor:
        return redirect('portal_login', token=token)
    
    pos = PurchaseOrder.objects.filter(vendor=vendor).prefetch_related('items').order_by('-created_at')
    return render(request, 'vendors/portal_history.html', {'vendor': vendor, 'pos': pos})

def portal_po_qr(request, token, po_number):
    # QR page should work with vendor theme using token in URL.
    # If vendor is also logged in (session), that's fine; token is still the source of truth.
    vendor = get_object_or_404(Vendor, portal_token=token, is_active=True)

    po = get_object_or_404(PurchaseOrder, po_number=po_number, vendor=vendor)

    host = request.get_host()
    proto = "https" if request.is_secure() else "http"
    qr_target_url = f"{proto}://{host}{reverse('portal_po_items', kwargs={'token': token, 'po_number': po.po_number})}"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=220x220&data={qr_target_url}"

    return render(request, 'vendors/portal_po_qr.html', {
        'vendor': vendor,
        'po': po,
        'qr_url': qr_url,
        'qr_target_url': qr_target_url,
    })

def portal_po_items(request, token, po_number):
    # Public page for QR scan (other device). Uses token + po_number, no session required.
    vendor = get_object_or_404(Vendor, portal_token=token, is_active=True)
    po = get_object_or_404(
        PurchaseOrder.objects.prefetch_related('items'),
        po_number=po_number,
        vendor=vendor,
    )

    if request.method == 'POST':
        allowed = {'Pending', 'Verified', 'Defective'}
        items = list(po.items.all())
        all_processed = True
        any_verified = False
        
        for item in items:
            new_status = (request.POST.get(f"status_{item.id}") or '').strip()
            if new_status and new_status in allowed:
                if item.status != new_status:
                    item.status = new_status
                    item.save(update_fields=['status'])
                
                if new_status == 'Pending':
                    all_processed = False
                else:
                    any_verified = True
            else:
                all_processed = False

        # Update overall PO status based on items
        if all_processed:
            po.status = "Verified"
        elif any_verified:
            po.status = "Received"
        po.save(update_fields=['status'])
        
        messages.success(request, 'Item statuses updated and PO status reflected.')

    return render(request, 'vendors/portal_po_items.html', {
        'vendor': vendor,
        'po': po,
        'qr_scan': True,
    })

def portal_logout(request, token):
    if 'vendor_id' in request.session:
        del request.session['vendor_id']
    return redirect('portal_login', token=token)



