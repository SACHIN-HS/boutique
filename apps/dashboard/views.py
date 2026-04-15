from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.utils import timezone
from django.db.models import Sum, F
from django.utils.text import slugify
import datetime

from .models import (
    Vendor, Product, PurchaseOrder, POItem, InventoryMove,
    Order, OrderItem, Tailor, TailoringJob, Expense
)


@login_required(login_url='login')
def dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'recent_logs': LogEntry.objects.select_related('user').order_by('-action_time')[:10],
        'total_orders': Order.objects.count(),
        'total_revenue': OrderItem.objects.aggregate(
            rev=Sum(F('price') * F('qty'))
        )['rev'] or 0,
        'total_vendors': Vendor.objects.count(),
        'total_products': Product.objects.count(),
    }
    return render(request, 'dashboard/dashboard.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'dashboard/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'dashboard/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── VENDOR ───────────────────────────────────────────────────────────────────

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
    return render(request, 'vendor_add.html')


@login_required(login_url='login')
def vendor_view(request):
    vendors = Vendor.objects.order_by('-created_at')
    return render(request, 'vendor_view.html', {'vendors': vendors})


@login_required(login_url='login')
def vendor_delete(request, pk):
    get_object_or_404(Vendor, pk=pk).delete()
    messages.success(request, 'Vendor deleted.')
    return redirect('vendor_view')


# ─── PRODUCT ──────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '').strip()
        sku = request.POST.get('sku', '').strip()
        description = request.POST.get('description', '').strip()
        qty = int(request.POST.get('qty', 0) or 0)
        discount = int(request.POST.get('discount', 0) or 0)
        sizes = ', '.join(request.POST.getlist('sizes'))
        colors = ', '.join(request.POST.getlist('colors'))
        slug_val = request.POST.get('slug', '').strip() or slugify(name)
        meta_title = request.POST.get('meta_title', '').strip()
        meta_tags = request.POST.get('meta_tags', '').strip()
        meta_description = request.POST.get('meta_description', '').strip()
        image = request.FILES.get('image')

        if name and category and sku and description:
            Product.objects.create(
                name=name, category=category, sku=sku, description=description,
                qty=qty, discount=discount, sizes=sizes, colors=colors,
                slug=slug_val, meta_title=meta_title, meta_tags=meta_tags,
                meta_description=meta_description, image=image,
            )
            messages.success(request, 'Product saved successfully!')
            return redirect('product_view')
        messages.error(request, 'Please fill required fields.')
    return render(request, 'product_add.html', {
        'sizes': ["XS","S","M","L","XL","XXL","XXXL","Free"],
        'colors': ["Red","Blue","Yellow","Green","Black","White","Pink","Purple"]
    })


@login_required(login_url='login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.category = request.POST.get('category', '').strip()
        product.sku = request.POST.get('sku', '').strip()
        product.description = request.POST.get('description', '').strip()
        product.qty = int(request.POST.get('qty', 0) or 0)
        product.discount = int(request.POST.get('discount', 0) or 0)
        product.sizes = ', '.join(request.POST.getlist('sizes'))
        product.colors = ', '.join(request.POST.getlist('colors'))
        product.slug = request.POST.get('slug', '').strip() or slugify(product.name)
        product.meta_title = request.POST.get('meta_title', '').strip()
        product.meta_tags = request.POST.get('meta_tags', '').strip()
        product.meta_description = request.POST.get('meta_description', '').strip()
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated!')
        return redirect('product_view')
    return render(request, 'product_edit.html', {
        'product': product,
        'sizes': ["XS","S","M","L","XL","XXL","XXXL","Free"],
        'colors': ["Red","Blue","Yellow","Green","Black","White","Pink","Purple"],
        'selected_sizes': product.sizes.split(', ') if product.sizes else [],
        'selected_colors': product.colors.split(', ') if product.colors else [],
    })


@login_required(login_url='login')
def product_view(request):
    products = Product.objects.order_by('-created_at')
    return render(request, 'product_view.html', {'products': products})


@login_required(login_url='login')
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, 'Product deleted.')
    return redirect('product_view')


# ─── PURCHASE ORDER ───────────────────────────────────────────────────────────

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
    return render(request, 'po_list.html', {
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
    return render(request, 'po_create.html', {'vendors': vendors})


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
    return render(request, 'po_receive.html', {'po': po})


# ─── SKU ──────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def sku_center(request):
    verified_pos = PurchaseOrder.objects.filter(status='Verified').prefetch_related('items').select_related('vendor')
    sku_out = None
    if request.method == 'POST':
        product_name = request.POST.get('product_name', '').strip()
        category = request.POST.get('category', '').strip()
        supplier_name = request.POST.get('supplier_name', '').strip()
        purchase_date = request.POST.get('purchase_date', '').strip()
        if product_name and category and supplier_name and purchase_date:
            def initials3(s):
                return ''.join(c for c in s.upper() if c.isalnum())[:3].ljust(3, 'X')
            cat_map = {'men': 'M', 'women': 'W', 'kids': 'K', 'jewelry': 'J'}
            cat1 = cat_map.get(category.lower(), category[0].upper() if category else 'X')
            try:
                dt = datetime.datetime.strptime(purchase_date, '%Y-%m-%d')
                yymmdd = dt.strftime('%y%m%d')
            except ValueError:
                yymmdd = '000000'
            sku_out = f"LAA{initials3(product_name)}{cat1}{initials3(supplier_name)}{yymmdd}"
    return render(request, 'sku_center.html', {'verified_pos': verified_pos, 'sku_out': sku_out})


@login_required(login_url='login')
def sku_mark_printed(request, item_pk):
    item = get_object_or_404(POItem, pk=item_pk)
    item.sku_printed = True
    item.save()
    messages.success(request, f'SKU marked as printed for {item.name}.')
    return redirect('sku_center')


# ─── INVENTORY ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def inventory(request):
    printed_items = POItem.objects.filter(
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
            item = get_object_or_404(POItem, pk=item_pk)
            if direction == 'to_website':
                InventoryMove.objects.create(po_item=item, from_location='store', to_location='website', qty=qty)
            elif direction == 'to_store':
                InventoryMove.objects.create(po_item=item, from_location='website', to_location='store', qty=qty)
            messages.success(request, 'Stock moved successfully!')
            return redirect('inventory')

    return render(request, 'inventory.html', {
        'store_items': store_items,
        'website_items': website_items,
    })


# ─── ORDER ────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def order_list(request):
    orders = Order.objects.prefetch_related('items').order_by('-created_at')
    tailors = Tailor.objects.order_by('name')
    return render(request, 'order_list.html', {'orders': orders, 'tailors': tailors})


@login_required(login_url='login')
def order_send_to_tailor(request, item_pk):
    item = get_object_or_404(OrderItem, pk=item_pk)
    if request.method == 'POST':
        tailor_id = request.POST.get('tailor')
        expected_at = request.POST.get('expected_at') or None
        expected_time = request.POST.get('expected_time', '').strip()
        notes = request.POST.get('notes', '').strip()
        tailor = get_object_or_404(Tailor, pk=tailor_id)
        job_no = f"JOB-{int(timezone.now().timestamp())}"
        TailoringJob.objects.create(
            job_no=job_no, order_item=item, tailor=tailor,
            qty=item.qty, expected_at=expected_at,
            expected_time=expected_time, notes=notes,
        )
        item.status = 'Sent to tailoring'
        item.save()
        messages.success(request, f'Sent to tailor {tailor.name}!')
    return redirect('order_list')


# ─── TAILORING ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def tailor_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        if name and phone and address:
            Tailor.objects.create(name=name, phone=phone, address=address)
            messages.success(request, 'Tailor saved!')
            return redirect('tailor_view')
        messages.error(request, 'Please fill all fields.')
    return render(request, 'tailor_add.html')


@login_required(login_url='login')
def tailor_view(request):
    tailors = Tailor.objects.order_by('-created_at')
    jobs = TailoringJob.objects.select_related('tailor', 'order_item__order').order_by('-created_at')
    return render(request, 'tailor_view.html', {'tailors': tailors, 'jobs': jobs})


@login_required(login_url='login')
def tailor_job_action(request, job_pk):
    job = get_object_or_404(TailoringJob, pk=job_pk)
    action = request.POST.get('action')
    if action == 'done':
        job.status = 'Done'
        job.done_at = timezone.now()
        job.order_item.status = 'Stitching done'
        job.order_item.save()
    elif action == 'delivered':
        job.status = 'Delivered'
        job.delivered_at = timezone.now()
        job.order_item.status = 'Delivered'
        job.order_item.save()
    job.save()
    messages.success(request, f'Job {job.job_no} updated to {job.status}.')
    return redirect('tailor_view')


# ─── ACCOUNTING ───────────────────────────────────────────────────────────────

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

    return render(request, 'accounting_pl.html', {
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
    return render(request, 'accounting_expenses.html', {'expenses': expenses})


@login_required(login_url='login')
def expense_delete(request, pk):
    get_object_or_404(Expense, pk=pk).delete()
    messages.success(request, 'Expense deleted.')
    return redirect('accounting_expenses')


# ─── LEGACY (kept for backward compat) ───────────────────────────────────────

@login_required(login_url='login')
def add_product(request):
    return redirect('product_add')


@login_required(login_url='login')
def add_category(request):
    return render(request, 'add_category.html')
