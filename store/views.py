from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AdminStore
from orders.models import Order
from itertools import groupby
from django.utils.timezone import localdate


def store_list(request):
    stores = AdminStore.objects.all()
    return render(request, 'store/store_list.html', {'stores': stores})


def store_detail(request, id):
    store = get_object_or_404(AdminStore, id=id)
    return render(request, 'store/store_front.html', {'store': store})


# ─────────────────────────────────────────────
# Store Orders — grouped by date
# Click store name → see all orders by date
# ─────────────────────────────────────────────
@login_required
def store_orders(request, id):
    store  = get_object_or_404(AdminStore, id=id)
    orders = Order.objects.filter(store=store).order_by('-created_at')

    # Group orders by date
    grouped = {}
    for order in orders:
        date_key = order.created_at.date()
        grouped.setdefault(date_key, []).append(order)

    return render(request, 'store/store_orders.html', {
        'store':   store,
        'grouped': grouped,   # dict: {date: [order, ...]}
    })