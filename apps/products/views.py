from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal, InvalidOperation
import json
import random
import datetime

from .models import Product, ProductImage, VariantCategory, VariantSize, VariantStyle, VariantGender
from apps.vendors.models import PurchaseOrder, PurchaseOrderItem


def _ensure_product_for_po_item(item: PurchaseOrderItem) -> None:
    """
    If a PO item has po_sku, ensure it exists in Product list.
    Uses po_sku as Product.sku (unique).
    """
    sku = (getattr(item, "po_sku", "") or "").strip()
    if not sku:
        return

    category = (getattr(item, "category", "") or "").strip() or "Uncategorized"
    name = (getattr(item, "item_code", "") or "").strip() or sku

    slug_base = slugify(sku) or slugify(name) or f"sku-{item.pk}"
    slug_val = slug_base
    if Product.objects.filter(slug=slug_val).exclude(sku=sku).exists():
        slug_val = f"{slug_base}-{item.pk}"

    sizes = (getattr(item, "size", "") or "").strip()
    # Normalize colors like "red" -> "Red" so UI checkboxes match
    raw_color = (getattr(item, "color", "") or "").strip()
    colors = raw_color.title() if raw_color else ""
    style_obj = getattr(item, "variant_style", None) if getattr(item, "variant_style_id", None) else None
    gender_obj = getattr(item, "variant_gender", None) if getattr(item, "variant_gender_id", None) else None
    reseller_price_val = getattr(item, "reseller_price", None)
    if reseller_price_val is None:
        reseller_price_val = Decimal("0")

    prod, created = Product.objects.get_or_create(
        sku=sku,
        defaults={
            "name": name,
            "category": category,
            "style": style_obj,
            "gender": gender_obj,
            "description": f"Auto-created from PO {item.purchase_order.po_number}",
            "qty": int(getattr(item, "qty", 0) or 0),
            "discount": 0,
            "reseller_price": reseller_price_val,
            "sizes": sizes,
            "colors": colors,
            "slug": slug_val,
            "meta_title": "",
            "meta_tags": "",
            "meta_description": "",
        },
    )

    if not created:
        changed = False
        if prod.name != name and name:
            prod.name = name
            changed = True
        if prod.category != category and category:
            prod.category = category
            changed = True
        qty_val = int(getattr(item, "qty", 0) or 0)
        if qty_val and prod.qty != qty_val:
            prod.qty = qty_val
            changed = True
        if sizes and not prod.sizes:
            prod.sizes = sizes
            changed = True
        if colors and not prod.colors:
            prod.colors = colors
            changed = True
        if gender_obj and prod.gender_id != getattr(gender_obj, "id", None):
            prod.gender = gender_obj
            changed = True
        if style_obj and prod.style_id != getattr(style_obj, "id", None):
            prod.style = style_obj
            changed = True
        try:
            if reseller_price_val is not None and prod.reseller_price != reseller_price_val:
                prod.reseller_price = reseller_price_val
                changed = True
        except Exception:
            pass
        if changed:
            prod.save()


def _code_from_text(text: str, length: int, fallback: str) -> str:
    raw = (text or "").strip().upper()
    cleaned = "".join(ch for ch in raw if ch.isalnum())
    if not cleaned:
        cleaned = fallback
    cleaned = cleaned[:length]
    if len(cleaned) < length:
        cleaned = cleaned.ljust(length, "X")
    return cleaned


def _reseller_price_to_int(price: Decimal) -> int:
    # SKU requirement example: 1500.00 -> 1500
    try:
        return int(price.quantize(Decimal("1")))
    except Exception:
        return int(price)


@login_required(login_url='login')
def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        category = request.POST.get('category', '').strip()
        style_id = request.POST.get('style', '').strip()
        gender_id = request.POST.get('gender', '').strip()
        sku = request.POST.get('sku', '').strip()
        description = request.POST.get('description', '').strip()
        qty = int(request.POST.get('qty', 0) or 0)
        discount = int(request.POST.get('discount', 0) or 0)
        reseller_price_raw = request.POST.get('reseller_price', '').strip()
        sizes = ', '.join(request.POST.getlist('sizes'))
        colors = ', '.join(request.POST.getlist('colors'))
        slug_base = slugify(sku) or slugify(name) or "product"
        slug_val = slug_base
        if Product.objects.filter(slug=slug_val).exists():
            slug_val = f"{slug_base}-{datetime.date.today().strftime('%y%m%d')}"
        meta_title = request.POST.get('meta_title', '').strip()
        meta_tags = request.POST.get('meta_tags', '').strip()
        meta_description = request.POST.get('meta_description', '').strip()
        image = request.FILES.get('image')
        images = request.FILES.getlist('images')

        if not image:
            messages.error(request, 'Main Product Image is required.')
            return redirect('product_add')
        if not images:
            messages.error(request, 'At least one image in Product Images (multiple) is required.')
            return redirect('product_add')

        style_obj = None
        if style_id:
            try:
                style_obj = VariantStyle.objects.filter(pk=int(style_id)).first()
            except (TypeError, ValueError):
                style_obj = None

        gender_obj = None
        if gender_id:
            try:
                gender_obj = VariantGender.objects.filter(pk=int(gender_id)).first()
            except (TypeError, ValueError):
                gender_obj = None
        try:
            reseller_price = Decimal(reseller_price_raw) if reseller_price_raw else Decimal("0")
        except (InvalidOperation, TypeError, ValueError):
            reseller_price = Decimal("0")

        if name and category and sku and description:
            product = Product.objects.create(
                name=name, category=category, gender=gender_obj, reseller_price=reseller_price,
                style=style_obj,
                sku=sku, description=description,
                qty=qty, discount=discount, sizes=sizes, colors=colors,
                slug=slug_val, meta_title=meta_title, meta_tags=meta_tags,
                meta_description=meta_description, image=image,
            )
            for f in images:
                ProductImage.objects.create(product=product, image=f)
            messages.success(request, 'Product saved successfully!')
            return redirect('product_view')
        messages.error(request, 'Please fill required fields.')
    return render(request, 'products/product_add.html', {
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'styles': VariantStyle.objects.all(),
        'genders': VariantGender.objects.all(),
        'sizes': VariantSize.objects.values_list('name', flat=True),
        'colors': ["Red", "Blue", "Yellow", "Green", "Black", "White", "Pink", "Purple"],
    })


@login_required(login_url='login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.category = request.POST.get('category', '').strip()
        style_id = request.POST.get('style', '').strip()
        gender_id = request.POST.get('gender', '').strip()
        # product.sku is read-only in edit mode
        product.description = request.POST.get('description', '').strip()
        product.qty = int(request.POST.get('qty', 0) or 0)
        product.discount = int(request.POST.get('discount', 0) or 0)
        reseller_price_raw = request.POST.get('reseller_price', '').strip()
        product.sizes = ', '.join(request.POST.getlist('sizes'))
        product.colors = ', '.join(request.POST.getlist('colors'))
        if not product.slug:
            product.slug = slugify(product.sku) or slugify(product.name) or f"product-{product.pk}"
        product.meta_title = request.POST.get('meta_title', '').strip()
        product.meta_tags = request.POST.get('meta_tags', '').strip()
        product.meta_description = request.POST.get('meta_description', '').strip()
        if gender_id:
            try:
                product.gender = VariantGender.objects.filter(pk=int(gender_id)).first()
            except (TypeError, ValueError):
                product.gender = None
        else:
            product.gender = None
        if style_id:
            try:
                product.style = VariantStyle.objects.filter(pk=int(style_id)).first()
            except (TypeError, ValueError):
                product.style = None
        else:
            product.style = None
        try:
            product.reseller_price = Decimal(reseller_price_raw) if reseller_price_raw else Decimal("0")
        except (InvalidOperation, TypeError, ValueError):
            product.reseller_price = Decimal("0")
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        for f in request.FILES.getlist("images"):
            ProductImage.objects.create(product=product, image=f)
        messages.success(request, 'Product updated!')
        return redirect('product_view')
    selected_sizes = [s.strip().lower() for s in (product.sizes or "").split(",") if s.strip()]
    selected_colors = [c.strip().lower() for c in (product.colors or "").split(",") if c.strip()]
    return render(request, 'products/product_edit.html', {
        'product': product,
        'categories': VariantCategory.objects.values_list('name', flat=True),
        'styles': VariantStyle.objects.all(),
        'genders': VariantGender.objects.all(),
        'sizes': VariantSize.objects.values_list('name', flat=True),
        'colors': ["Red", "Blue", "Yellow", "Green", "Black", "White", "Pink", "Purple"],
        'selected_sizes': selected_sizes,
        'selected_colors': selected_colors,
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
    verified_pos = (
        PurchaseOrder.objects.filter(status="Verified")
        .select_related("vendor")
        .prefetch_related("items", "items__variant_style", "items__variant_gender")
        .order_by("-created_at")
    )

    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()
    if date_from:
        verified_pos = verified_pos.filter(created_at__date__gte=date_from)
    if date_to:
        verified_pos = verified_pos.filter(created_at__date__lte=date_to)

    # Backfill Products list from any generated PO SKUs shown on this page.
    items_with_sku = (
        PurchaseOrderItem.objects.filter(purchase_order__in=verified_pos)
        .exclude(po_sku="")
        .select_related("purchase_order")
    )
    existing_skus = set(Product.objects.filter(sku__in=items_with_sku.values_list("po_sku", flat=True)).values_list("sku", flat=True))
    for it in items_with_sku:
        if it.po_sku and it.po_sku not in existing_skus:
            _ensure_product_for_po_item(it)
            existing_skus.add(it.po_sku)

    return render(
        request,
        "products/sku_center.html",
        {
            "verified_pos": verified_pos,
            "date_from": date_from,
            "date_to": date_to,
            "styles": VariantStyle.objects.all(),
            "categories": VariantCategory.objects.all(),
        },
    )


@csrf_protect
@require_POST
@login_required(login_url="login")
def sku_update_item(request):
    """
    JSON:
      { "id": 123, "variant_style_id": 5, "category": "REGULAR" }
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON payload."}, status=400)

    try:
        item_id = int(payload.get("id"))
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid item id."}, status=400)

    item = get_object_or_404(PurchaseOrderItem, pk=item_id)

    style_id = payload.get("variant_style_id", None)
    if style_id in ("", None):
        item.variant_style = None
    else:
        try:
            style_id_int = int(style_id)
        except Exception:
            return JsonResponse({"ok": False, "error": "Invalid style id."}, status=400)
        item.variant_style = get_object_or_404(VariantStyle, pk=style_id_int)

    category = (payload.get("category") or "").strip()
    item.category = category

    item.save(update_fields=["variant_style", "category"])
    return JsonResponse(
        {
            "ok": True,
            "id": item.pk,
            "variant_style": getattr(item.variant_style, "name", "") if item.variant_style_id else "",
            "category": item.category,
        }
    )


@login_required(login_url="login")
def sku_print(request):
    """
    Printable view.
    Supports:
      - GET ?payload=<base64url(json)> where json = {"items":[{"id":1,"count":2}, ...]}
      - GET ?ids=1,2,3 (fallback, count=1 each)
    """
    ids = []
    counts = {}

    payload_b64 = (request.GET.get("payload") or "").strip()
    if payload_b64:
        import base64

        def _b64url_decode(s: str) -> str:
            s = s.replace("-", "+").replace("_", "/")
            pad = "=" * ((4 - (len(s) % 4)) % 4)
            return base64.b64decode((s + pad).encode("utf-8")).decode("utf-8")

        try:
            payload = json.loads(_b64url_decode(payload_b64))
            for row in payload.get("items") or []:
                try:
                    item_id = int(row.get("id"))
                except Exception:
                    continue
                try:
                    count = int(row.get("count") or 1)
                except Exception:
                    count = 1
                if count < 1:
                    count = 1
                if count > 500:
                    count = 500
                ids.append(item_id)
                counts[item_id] = count
        except Exception:
            ids = []
            counts = {}

    if not ids:
        raw_ids = (request.GET.get("ids") or "").strip()
        for part in raw_ids.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                item_id = int(part)
            except Exception:
                continue
            ids.append(item_id)
            counts[item_id] = 1

    items = list(
        PurchaseOrderItem.objects.filter(pk__in=ids)
        .select_related("purchase_order__vendor", "variant_style", "variant_gender")
        .order_by("purchase_order__po_number", "pk")
    )
    by_id = {i.pk: i for i in items}

    labels = []
    for item_id in ids:
        item = by_id.get(item_id)
        if not item:
            continue
        for _ in range(counts.get(item_id, 1)):
            labels.append(item)

    return render(request, "products/sku_print.html", {"labels": labels})


@login_required(login_url="login")
def sku_item_label(request, item_pk):
    """
    Opens the same label print view for a single item.
    Optional GET param: ?count=5
    """
    item = get_object_or_404(
        PurchaseOrderItem.objects.select_related("purchase_order__vendor", "variant_style", "variant_gender"),
        pk=item_pk,
    )
    try:
        count = int(request.GET.get("count") or 1)
    except Exception:
        count = 1
    if count < 1:
        count = 1
    if count > 500:
        count = 500

    labels = [item for _ in range(count)]
    return render(request, "products/sku_print.html", {"labels": labels})

@csrf_protect
@require_POST
@login_required(login_url="login")
def sku_generate(request):
    """
    Receives JSON payload:
      { "items": [ { "id": 123, "reseller_price": "1500" }, ... ] }

    Generates:
      - po_sku: STYLE(3)-CATEGORY(1)-VENDOR(3)-YY-MM
      - reseller_sku (Cost SKU): random(1) + reseller_price_int + random(1)
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "Invalid JSON payload."}, status=400)

    items_in = payload.get("items") or []
    if not isinstance(items_in, list) or not items_in:
        return JsonResponse({"ok": False, "error": "No items provided."}, status=400)

    ids = []
    reseller_price_map = {}
    for row in items_in:
        try:
            item_id = int(row.get("id"))
        except Exception:
            continue
        ids.append(item_id)
        reseller_price_map[item_id] = row.get("reseller_price")

    if not ids:
        return JsonResponse({"ok": False, "error": "No valid item ids provided."}, status=400)

    qs = (
        PurchaseOrderItem.objects.filter(pk__in=ids)
        .select_related("purchase_order__vendor", "variant_style")
    )

    updated = []
    now = datetime.date.today()
    for item in qs:
        po = item.purchase_order
        vendor = po.vendor if po else None

        style_name = getattr(item.variant_style, "name", "") if item.variant_style_id else ""
        vendor_name = getattr(vendor, "name", "") if vendor else ""
        category_name = (item.category or "").strip()

        style_code = _code_from_text(style_name, 3, "STY")
        category_code = _code_from_text(category_name, 1, "C")
        vendor_code = _code_from_text(vendor_name, 3, "VND")

        base_date = po.created_at.date() if po and getattr(po, "created_at", None) else now
        yy = base_date.year % 100
        mm = base_date.month

        sku1 = f"{style_code}-{category_code}-{vendor_code}-{yy:02d}-{mm:02d}"

        raw_price = reseller_price_map.get(item.pk, None)
        try:
            reseller_price = Decimal(str(raw_price)) if raw_price is not None else item.reseller_price
        except (InvalidOperation, TypeError, ValueError):
            reseller_price = item.reseller_price

        if reseller_price is None:
            reseller_price = Decimal("0")

        # Cost SKU must be generated from Unit Price (not reseller price)
        price_int = _reseller_price_to_int(item.unit_price)
        a = random.randint(1, 9)
        b = random.randint(0, 9)
        sku2 = f"{a}{price_int}{b}"

        item.po_sku = sku1
        item.reseller_price = reseller_price
        item.reseller_sku = sku2
        item.save(update_fields=["po_sku", "reseller_price", "reseller_sku"])
        _ensure_product_for_po_item(item)

        updated.append(
            {
                "id": item.pk,
                "po_sku": item.po_sku,
                "reseller_price": str(item.reseller_price),
                "reseller_sku": item.reseller_sku,
            }
        )

    messages.success(request, f"Successfully generated SKU for {len(updated)} items.")
    return JsonResponse({"ok": True, "updated": updated})



@login_required(login_url='login')
def sku_mark_printed(request, item_pk):
    item = get_object_or_404(PurchaseOrderItem, pk=item_pk)
    item.sku_printed = True
    item.save()
    messages.success(request, f'SKU marked as printed for {item.name}.')
    return redirect('sku_center')


@login_required(login_url='login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('add_category')

        slug_value = request.POST.get('slug', '').strip() or slugify(name)
        if VariantCategory.objects.filter(name__iexact=name).exists():
            messages.warning(request, f'Category "{name}" already exists.')
        else:
            VariantCategory.objects.create(name=name, slug=slug_value)
            messages.success(request, f'Category "{name}" saved successfully.')
        return redirect('add_category')

    return render(request, 'products/add_category.html', {
        'categories': VariantCategory.objects.all(),
    })


@login_required(login_url='login')
def edit_category(request, pk):
    category = get_object_or_404(VariantCategory, pk=pk)
    if request.method == 'GET':
        return render(request, 'products/add_category.html', {
            'categories': VariantCategory.objects.all(),
            'edit_category': category,
        })
    if request.method != 'POST':
        return redirect('add_category')

    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'Category name is required.')
        return redirect('add_category')

    slug_value = request.POST.get('slug', '').strip() or slugify(name)

    if VariantCategory.objects.filter(name__iexact=name).exclude(pk=category.pk).exists():
        messages.warning(request, f'Category "{name}" already exists.')
        return redirect('add_category')

    if VariantCategory.objects.filter(slug=slug_value).exclude(pk=category.pk).exists():
        messages.warning(request, f'Slug "{slug_value}" is already used.')
        return redirect('add_category')

    category.name = name
    category.slug = slug_value
    category.save()
    messages.success(request, f'Category "{name}" updated successfully.')
    return redirect('add_category')


@login_required(login_url='login')
def delete_category(request, pk):
    category = get_object_or_404(VariantCategory, pk=pk)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully.')
    return redirect('add_category')


@login_required(login_url='login')
def add_size(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Size name is required.')
            return redirect('add_size')

        code = request.POST.get('code', '').strip()
        if VariantSize.objects.filter(name__iexact=name).exists():
            messages.warning(request, f'Size "{name}" already exists.')
        else:
            VariantSize.objects.create(name=name, code=code)
            messages.success(request, f'Size "{name}" saved successfully.')
        return redirect('add_size')

    return render(request, 'products/add_size.html', {
        'sizes': VariantSize.objects.all(),
    })


@login_required(login_url='login')
def edit_size(request, pk):
    size = get_object_or_404(VariantSize, pk=pk)
    if request.method == 'GET':
        return render(request, 'products/add_size.html', {
            'sizes': VariantSize.objects.all(),
            'edit_size': size,
        })
    if request.method != 'POST':
        return redirect('add_size')

    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'Size name is required.')
        return redirect('add_size')

    code = request.POST.get('code', '').strip()
    if VariantSize.objects.filter(name__iexact=name).exclude(pk=size.pk).exists():
        messages.warning(request, f'Size "{name}" already exists.')
        return redirect('add_size')

    size.name = name
    size.code = code
    size.save()
    messages.success(request, f'Size "{name}" updated successfully.')
    return redirect('add_size')


@login_required(login_url='login')
def delete_size(request, pk):
    size = get_object_or_404(VariantSize, pk=pk)
    if request.method == 'POST':
        size_name = size.name
        size.delete()
        messages.success(request, f'Size "{size_name}" deleted successfully.')
    return redirect('add_size')


@login_required(login_url="login")
def add_style(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "Style name is required.")
            return redirect("add_style")

        slug_value = request.POST.get("slug", "").strip() or slugify(name)
        if VariantStyle.objects.filter(name__iexact=name).exists():
            messages.warning(request, f'Style "{name}" already exists.')
        else:
            VariantStyle.objects.create(name=name, slug=slug_value)
            messages.success(request, f'Style "{name}" saved successfully.')
        return redirect("add_style")

    return render(
        request,
        "products/add_style.html",
        {
            "styles": VariantStyle.objects.all(),
        },
    )


@login_required(login_url="login")
def edit_style(request, pk):
    style = get_object_or_404(VariantStyle, pk=pk)
    if request.method == "GET":
        return render(
            request,
            "products/add_style.html",
            {
                "styles": VariantStyle.objects.all(),
                "edit_style": style,
            },
        )
    if request.method != "POST":
        return redirect("add_style")

    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Style name is required.")
        return redirect("add_style")

    slug_value = request.POST.get("slug", "").strip() or slugify(name)
    if VariantStyle.objects.filter(name__iexact=name).exclude(pk=style.pk).exists():
        messages.warning(request, f'Style "{name}" already exists.')
        return redirect("add_style")
    if VariantStyle.objects.filter(slug=slug_value).exclude(pk=style.pk).exists():
        messages.warning(request, f'Slug "{slug_value}" is already used.')
        return redirect("add_style")

    style.name = name
    style.slug = slug_value
    style.save()
    messages.success(request, f'Style "{name}" updated successfully.')
    return redirect("add_style")


@login_required(login_url="login")
def delete_style(request, pk):
    style = get_object_or_404(VariantStyle, pk=pk)
    if request.method == "POST":
        name = style.name
        style.delete()
        messages.success(request, f'Style "{name}" deleted successfully.')
    return redirect("add_style")


@login_required(login_url="login")
def add_gender(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "Gender name is required.")
            return redirect("add_gender")

        slug_value = request.POST.get("slug", "").strip() or slugify(name)
        if VariantGender.objects.filter(name__iexact=name).exists():
            messages.warning(request, f'Gender "{name}" already exists.')
        else:
            VariantGender.objects.create(name=name, slug=slug_value)
            messages.success(request, f'Gender "{name}" saved successfully.')
        return redirect("add_gender")

    return render(
        request,
        "products/add_gender.html",
        {
            "genders": VariantGender.objects.all(),
        },
    )


@login_required(login_url="login")
def edit_gender(request, pk):
    gender = get_object_or_404(VariantGender, pk=pk)
    if request.method == "GET":
        return render(
            request,
            "products/add_gender.html",
            {
                "genders": VariantGender.objects.all(),
                "edit_gender": gender,
            },
        )
    if request.method != "POST":
        return redirect("add_gender")

    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Gender name is required.")
        return redirect("add_gender")

    slug_value = request.POST.get("slug", "").strip() or slugify(name)
    if VariantGender.objects.filter(name__iexact=name).exclude(pk=gender.pk).exists():
        messages.warning(request, f'Gender "{name}" already exists.')
        return redirect("add_gender")
    if VariantGender.objects.filter(slug=slug_value).exclude(pk=gender.pk).exists():
        messages.warning(request, f'Slug "{slug_value}" is already used.')
        return redirect("add_gender")

    gender.name = name
    gender.slug = slug_value
    gender.save()
    messages.success(request, f'Gender "{name}" updated successfully.')
    return redirect("add_gender")


@login_required(login_url="login")
def delete_gender(request, pk):
    gender = get_object_or_404(VariantGender, pk=pk)
    if request.method == "POST":
        name = gender.name
        gender.delete()
        messages.success(request, f'Gender "{name}" deleted successfully.')
    return redirect("add_gender")
