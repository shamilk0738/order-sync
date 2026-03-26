from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product/product_list.html', {
        'products': products
    })



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    total = None

    
    store_id = request.GET.get('store_id') or request.POST.get('store_id', '')

    if request.method == "POST":
        quantity = int(request.POST.get('quantity'))
        total = quantity * product.rate

    return render(request, 'product/product_item.html', {
        'product': product,
        'total': total,
        'store_id': store_id,  
    })