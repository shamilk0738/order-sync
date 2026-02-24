# orders/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from .models import Order, OrderItem
from store.models import AdminStore


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ('product', 'quantity', 'subtotal_display')
    fields          = ('product', 'quantity', 'subtotal_display')
    can_delete      = False

    def subtotal_display(self, obj):
        return f"₹ {obj.subtotal}"
    subtotal_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ('order_name', 'user', 'store', 'status',
                       'total_price', 'created_at', 'estimate_bill_link')
    list_filter     = ('status', 'store')
    search_fields   = ('order_name', 'user__username')
    inlines         = [OrderItemInline]
    readonly_fields = ('total_price', 'created_at')

    def estimate_bill_link(self, obj):
        url = f"/admin/orders/order/{obj.id}/estimate-bill/"
        return format_html('<a href="{}" target="_blank">📄 Estimate Bill</a>', url)
    estimate_bill_link.short_description = "Estimate Bill"

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('<int:order_id>/estimate-bill/',
                 self.admin_site.admin_view(self.estimate_bill_view),
                 name='order_estimate_bill'),
        ]
        return custom + urls

    def estimate_bill_view(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        context = {
            **self.admin_site.each_context(request),
            'order': order,
            'items': order.items.select_related('product').all(),
        }
        return render(request, 'admin/orders/estimate_bill.html', context)

# ❌ AdminStore class ഇവിടെ വേണ്ട — store/admin.py-ൽ add ചെയ്യണം