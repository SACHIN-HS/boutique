from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Order, OrderItem
from apps.tailoring.models import Tailor, TailoringJob


@login_required(login_url='login')
def order_list(request):
    orders = Order.objects.prefetch_related('items').order_by('-created_at')
    tailors = Tailor.objects.order_by('name')
    return render(request, 'orders/order_list.html', {'orders': orders, 'tailors': tailors})


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
