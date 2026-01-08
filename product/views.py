from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product/product_list.html', {
        'products': products
    })


# Product detail page
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    total = None

    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        total = quantity * product.rate

    return render(request, 'product/product_item.html', {
        'product': product,
        'total': total
    })