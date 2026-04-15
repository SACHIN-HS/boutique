from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Tailor, TailoringJob


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
    return render(request, 'tailoring/tailor_add.html')


@login_required(login_url='login')
def tailor_view(request):
    tailors = Tailor.objects.order_by('-created_at')
    jobs = TailoringJob.objects.select_related('tailor', 'order_item__order').order_by('-created_at')
    return render(request, 'tailoring/tailor_view.html', {'tailors': tailors, 'jobs': jobs})


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
