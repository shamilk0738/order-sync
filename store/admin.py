# store/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from .models import AdminStore


@admin.register(AdminStore)
class AdminStoreAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'view_orders_link')

    def view_orders_link(self, obj):
        url = f"/admin/orders/store/{obj.id}/orders/"
        return format_html('<a href="{}">📋 View Orders & Bills</a>', url)
    view_orders_link.short_description = "Orders"

    def get_urls(self):
        from orders.models import Order
        urls = super().get_urls()
        custom = [
            path('<int:store_id>/orders/',
                 self.admin_site.admin_view(self.store_orders_view),
                 name='store_orders_list'),
        ]
        return custom + urls

    def store_orders_view(self, request, store_id):
        from orders.models import Order
        store  = get_object_or_404(AdminStore, id=store_id)
        orders = Order.objects.filter(store=store).order_by('-created_at')
        context = {
            **self.admin_site.each_context(request),
            'store':  store,
            'orders': orders,
        }
        return render(request, 'admin/orders/store_orders.html', context)