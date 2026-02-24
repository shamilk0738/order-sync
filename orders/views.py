from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from store.models import AdminStore
from product.models import Product


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


@login_required
def orders_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/orders_list.html', {'orders': orders})


@login_required
def order_detail(request, id):
    order    = get_object_or_404(Order, id=id)
    products = Product.objects.filter(stock__gt=0)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_item':
            item_id = request.POST.get('item_id')
            OrderItem.objects.filter(id=item_id, order=order).delete()
            order.recalculate_total()

        elif action == 'update_qty':
            item_id = request.POST.get('item_id')
            new_qty = request.POST.get('quantity', 0)
            try:
                new_qty = int(new_qty)
            except ValueError:
                new_qty = 0
            if new_qty > 0:
                item = get_object_or_404(OrderItem, id=item_id, order=order)
                item.quantity = new_qty
                item.save()
                order.recalculate_total()
            else:
                OrderItem.objects.filter(id=item_id, order=order).delete()
                order.recalculate_total()

        elif action == 'add_product':
            product_id = request.POST.get('product_id')
            new_qty    = request.POST.get('new_qty', 0)
            try:
                new_qty = int(new_qty)
            except ValueError:
                new_qty = 0
            if new_qty > 0:
                product  = get_object_or_404(Product, id=product_id)
                existing = OrderItem.objects.filter(order=order, product=product).first()
                if existing:
                    existing.quantity += new_qty
                    existing.save()
                else:
                    OrderItem.objects.create(order=order, product=product, quantity=new_qty)
                order.recalculate_total()

        return redirect('order_detail', order.id)

    return render(request, 'orders/order_detail.html', {
        'order':    order,
        'products': products,
    })