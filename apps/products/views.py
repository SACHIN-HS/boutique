from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
import datetime

from .models import Product
from apps.vendors.models import PurchaseOrder, POItem


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
    return render(request, 'products/product_add.html', {
        'sizes': ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "Free"],
        'colors': ["Red", "Blue", "Yellow", "Green", "Black", "White", "Pink", "Purple"],
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
    return render(request, 'products/product_edit.html', {
        'product': product,
        'sizes': ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "Free"],
        'colors': ["Red", "Blue", "Yellow", "Green", "Black", "White", "Pink", "Purple"],
    })


@login_required(login_url='login')
def product_view(request):
    products = Product.objects.order_by('-created_at')
    return render(request, 'products/product_view.html', {'products': products})


@login_required(login_url='login')
def product_delete(request, pk):
    get_object_or_404(Product, pk=pk).delete()
    messages.success(request, 'Product deleted.')
    return redirect('product_view')


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
    return render(request, 'products/sku_center.html', {'verified_pos': verified_pos, 'sku_out': sku_out})


@login_required(login_url='login')
def sku_mark_printed(request, item_pk):
    item = get_object_or_404(POItem, pk=item_pk)
    item.sku_printed = True
    item.save()
    messages.success(request, f'SKU marked as printed for {item.name}.')
    return redirect('sku_center')


@login_required(login_url='login')
def add_category(request):
    return render(request, 'products/add_category.html')
