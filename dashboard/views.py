from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def admin_dashboard(request):
    from orders.models import Order, OrderItem
    from store.models import AdminStore
    from product.models import Product

    today = timezone.now().date()

    
    total_orders   = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    staff_members  = User.objects.filter(is_active=True).count()
    stores_visited = Order.objects.filter(
        created_at__date=today
    ).values('store').distinct().count()

    
    latest_orders = (
        Order.objects
        .select_related('store', 'user')
        .order_by('-created_at')[:5]
    )

    
    try:
        from attendance.models import Attendance
        today_present = Attendance.objects.filter(
            date=today, status='present'
        ).count()
        month_start = today.replace(day=1)
        month_total = Attendance.objects.filter(
            date__gte=month_start, date__lte=today
        ).count()
        month_present = Attendance.objects.filter(
            date__gte=month_start, date__lte=today, status='present'
        ).count()
        monthly_pct = round((month_present / month_total * 100)) if month_total else 0
    except Exception:
        today_present = 0
        monthly_pct   = 0

    
    try:
        top_products = (
            OrderItem.objects
            .values('product__name')
            .annotate(total_qty=Sum('quantity'))
            .order_by('-total_qty')[:4]
        )
    except Exception:
        top_products = []

    # Max qty for progress bar width
    max_qty = top_products[0]['total_qty'] if top_products else 1

    
    visit_days   = []
    visit_counts = []
    for i in range(4, -1, -1):
        d = today - timedelta(days=i)
        cnt = Order.objects.filter(created_at__date=d).count()
        visit_days.append(d.strftime('%a'))
        visit_counts.append(cnt)

    return render(request, 'dashboard/dashboard.html', {
        'total_orders':   total_orders,
        'pending_orders': pending_orders,
        'staff_members':  staff_members,
        'stores_visited': stores_visited,
        'latest_orders':  latest_orders,
        'today_present':  today_present,
        'monthly_pct':    monthly_pct,
        'top_products':   top_products,
        'max_qty':        max_qty,
        'visit_days':     visit_days,
        'visit_counts':   visit_counts,
    })