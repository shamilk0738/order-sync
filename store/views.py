from django.shortcuts import render, get_object_or_404
from .models import AdminStore

def store_list(request):
    stores = AdminStore.objects.all()
    return render(request, 'store/store_list.html', {
        'stores': stores
    })

def store_detail(request, id):
    store = get_object_or_404(AdminStore, id=id)
    return render(request, 'store/store_front.html', {
        'store': store
    })
