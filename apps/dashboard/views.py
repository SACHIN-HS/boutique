from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.db.models import Sum, F

from apps.orders.models import Order, OrderItem
from apps.vendors.models import Vendor
from apps.products.models import Product


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
