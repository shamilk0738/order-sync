from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from store.models import AdminStore
from product.models import Product


# ─────────────────────────────────────────────
# 1. CREATE ORDER PAGE
#    GET  → show stores dropdown + products
#    POST → save order
# ─────────────────────────────────────────────
@login_required
def create_order(request):
    stores   = AdminStore.objects.all()
    store_id = request.GET.get('store_id') or request.POST.get('store')
    store    = None
    products = []

    if store_id:
        store    = get_object_or_404(AdminStore, id=store_id)
        products = Product.objects.filter(stock__gt=0)

    if request.method == 'POST' and store:
        # Collect items that have quantity > 0
        items_to_save = []
        for product in Product.objects.filter(stock__gt=0):
            qty = request.POST.get(f'qty_{product.id}', 0)
            try:
                qty = int(qty)
            except ValueError:
                qty = 0
            if qty > 0:
                items_to_save.append((product, qty))

        if items_to_save:
            order = Order.objects.create(
                user=request.user,
                store=store,
                order_name=f"Order - {store.store_name}",
                status='pending',
            )
            for product, qty in items_to_save:
                OrderItem.objects.create(order=order, product=product, quantity=qty)
            order.recalculate_total()
            return redirect('order_detail', order.id)

    return render(request, 'orders/create_order.html', {
        'stores':   stores,
        'store':    store,
        'products': products,
    })


# ─────────────────────────────────────────────
# 2. ALL ORDERS LIST
# ─────────────────────────────────────────────
@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders_list.html', {'orders': orders})


# ─────────────────────────────────────────────
# 3. SINGLE ORDER DETAIL / ESTIMATE
# ─────────────────────────────────────────────
@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})