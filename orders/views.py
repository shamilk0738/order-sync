from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from product.models import Product

@login_required
def create_order(request):
    products = Product.objects.all()

    if request.method == "POST":
        order_name = request.POST.get("order_name")

        order = Order.objects.create(
            user=request.user,
            order_name=order_name
        )

        for product in products:
            qty = request.POST.get(f"qty_{product.id}")

            if qty and int(qty) > 0:
                # Optional: stock check
                if int(qty) <= product.stock:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=int(qty)
                    )

                    # Reduce stock (optional)
                    product.stock -= int(qty)
                    product.save()

        return redirect("orders_list")

    return render(request, "orders/create_order.html", {
        "products": products
    })


def orders_list(request):
    orders = Order.objects.select_related("user").prefetch_related("items__product")
    return render(request, "orders/orders_list.html", {
        "orders": orders
    })


def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related("items__product"),
        id=order_id
    )
    return render(request, "orders/order_detail.html", {
        "order": order
    })
