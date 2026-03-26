from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, date
from orders.models import Order, OrderItem
from store.models import AdminStore
from product.models import Product



def get_period(request, default='today'):
    period = request.GET.get('period', default)
    today  = timezone.now().date()

    if period == 'today':
        return period, today, today, 'Today'
    elif period == 'week':
        return period, today - timedelta(days=6), today, 'Last 7 Days'
    elif period == 'month':
        return period, today.replace(day=1), today, 'This Month'
    elif period == 'custom':
        try:
            start = date.fromisoformat(request.GET.get('start', str(today)))
            end   = date.fromisoformat(request.GET.get('end',   str(today)))
            return period, start, end, f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"
        except ValueError:
            pass
    return 'today', today, today, 'Today'



@login_required
def sales_report(request):
    period, start, end, label = get_period(request, default='today')

    orders_qs = Order.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end,
    )

    # Summary cards
    total_orders     = orders_qs.count()
    total_revenue    = orders_qs.aggregate(rev=Sum('total_price'))['rev'] or 0
    pending_orders   = orders_qs.filter(status='pending').count()
    completed_orders = orders_qs.filter(status='complete').count()

    # Daily breakdown
    daily = (
        orders_qs
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'), revenue=Sum('total_price'))
        .order_by('day')
    )

    chart_labels  = [str(d['day'])            for d in daily]
    chart_orders  = [d['count']               for d in daily]
    chart_revenue = [float(d['revenue'] or 0) for d in daily]

    # Store-wise breakdown
    store_breakdown = (
        orders_qs
        .values('store__store_name')
        .annotate(count=Count('id'), revenue=Sum('total_price'))
        .order_by('-revenue')
    )

    # Latest 10 orders
    latest_orders = orders_qs.select_related('store', 'user').order_by('-created_at')[:10]

    return render(request, 'reports/sales_report.html', {
        'period':           period,
        'label':            label,
        'start':            start,
        'end':              end,
        'total_orders':     total_orders,
        'total_revenue':    total_revenue,
        'pending_orders':   pending_orders,
        'completed_orders': completed_orders,
        'daily':            daily,
        'chart_labels':     chart_labels,
        'chart_orders':     chart_orders,
        'chart_revenue':    chart_revenue,
        'store_breakdown':  store_breakdown,
        'latest_orders':    latest_orders,
    })



@login_required
def staff_performance_report(request):
    period, start, end, label = get_period(request, default='month')

    orders_qs = Order.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end,
    )

    
    staff_stats = (
        orders_qs
        .values('user__id', 'user__username', 'user__first_name', 'user__last_name')
        .annotate(
            total_orders     = Count('id'),
            total_revenue    = Sum('total_price'),
            completed_orders = Count('id', filter=Q(status='complete')),
            pending_orders   = Count('id', filter=Q(status='pending')),
        )
        .order_by('-total_orders')
    )

    staff_list = []
    for s in staff_stats:
        total = s['total_orders'] or 1
        s['completion_rate'] = round((s['completed_orders'] / total) * 100)
        s['full_name'] = (
            f"{s['user__first_name']} {s['user__last_name']}".strip()
            or s['user__username']
        )
        staff_list.append(s)

    # Overall summary
    total_orders_all  = orders_qs.count()
    total_revenue_all = orders_qs.aggregate(r=Sum('total_price'))['r'] or 0
    total_staff       = len(staff_list)
    top_performer     = staff_list[0] if staff_list else None

    # Chart data
    chart_labels  = [s['full_name']                 for s in staff_list]
    chart_orders  = [s['total_orders']              for s in staff_list]
    chart_revenue = [float(s['total_revenue'] or 0) for s in staff_list]

    # Daily trend for top 3 staff
    top3      = staff_list[:3]
    all_dates = []
    cur       = start
    while cur <= end:
        all_dates.append(str(cur))
        cur += timedelta(days=1)

    trend_data = []
    for s in top3:
        daily_counts = (
            orders_qs
            .filter(user__id=s['user__id'])
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        daily_map = {str(d['day']): d['count'] for d in daily_counts}
        trend_data.append({
            'name':   s['full_name'],
            'counts': [daily_map.get(d, 0) for d in all_dates],
        })

    recent_orders = orders_qs.select_related('user', 'store').order_by('-created_at')[:20]

    return render(request, 'reports/staff_performance.html', {
        'period':            period,
        'label':             label,
        'start':             start,
        'end':               end,
        'staff_list':        staff_list,
        'total_orders_all':  total_orders_all,
        'total_revenue_all': total_revenue_all,
        'total_staff':       total_staff,
        'top_performer':     top_performer,
        'chart_labels':      chart_labels,
        'chart_orders':      chart_orders,
        'chart_revenue':     chart_revenue,
        'all_dates':         all_dates,
        'trend_data':        trend_data,
        'recent_orders':     recent_orders,
    })



@login_required
def store_report(request):
    period, start, end, label = get_period(request, default='month')
    store_id = request.GET.get('store_id', '')

    orders_qs = Order.objects.filter(
        created_at__date__gte=start,
        created_at__date__lte=end,
    )

    
    store_summary = (
        orders_qs
        .values('store__id', 'store__store_name')
        .annotate(
            total_orders  = Count('id'),
            total_revenue = Sum('total_price'),
            completed     = Count('id', filter=Q(status='complete')),
            pending       = Count('id', filter=Q(status='pending')),
        )
        .order_by('-total_revenue')
    )

    total_revenue_all = orders_qs.aggregate(r=Sum('total_price'))['r'] or 0
    total_orders_all  = orders_qs.count()
    total_stores      = store_summary.count()

    chart_labels  = [s['store__store_name'] or '—' for s in store_summary]
    chart_revenue = [float(s['total_revenue'] or 0) for s in store_summary]
    chart_orders  = [s['total_orders']              for s in store_summary]

    # Selected store drill-down
    selected_store = None
    store_daily    = []
    store_orders   = []
    store_products = []
    s_chart_labels = []
    s_chart_orders = []
    s_chart_rev    = []

    if store_id:
        selected_store = get_object_or_404(AdminStore, id=store_id)
        sq             = orders_qs.filter(store=selected_store)

        store_daily = (
            sq.annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'), revenue=Sum('total_price'))
            .order_by('day')
        )

        s_chart_labels = [str(d['day'])            for d in store_daily]
        s_chart_orders = [d['count']               for d in store_daily]
        s_chart_rev    = [float(d['revenue'] or 0) for d in store_daily]

        store_orders = sq.select_related('user').order_by('-created_at')[:15]

        store_products = (
            OrderItem.objects
            .filter(
                order__store=selected_store,
                order__created_at__date__gte=start,
                order__created_at__date__lte=end,
            )
            .values('product__name', 'product__rate')
            .annotate(
                total_qty     = Sum('quantity'),
                total_revenue = Sum(F('quantity') * F('product__rate')),
            )
            .order_by('-total_qty')[:8]
        )

    return render(request, 'reports/store_report.html', {
        'period':            period,
        'label':             label,
        'start':             start,
        'end':               end,
        'all_stores':        AdminStore.objects.all(),
        'store_summary':     store_summary,
        'total_revenue_all': total_revenue_all,
        'total_orders_all':  total_orders_all,
        'total_stores':      total_stores,
        'selected_store':    selected_store,
        'store_id':          store_id,
        'store_daily':       store_daily,
        'store_orders':      store_orders,
        'store_products':    store_products,
        'chart_labels':      chart_labels,
        'chart_revenue':     chart_revenue,
        'chart_orders':      chart_orders,
        's_chart_labels':    s_chart_labels,
        's_chart_orders':    s_chart_orders,
        's_chart_rev':       s_chart_rev,
    })



@login_required
def product_report(request):
    period, start, end, label = get_period(request, default='month')
    LOW_STOCK = 10

    # Best selling products
    best_selling = (
        OrderItem.objects
        .filter(
            order__created_at__date__gte=start,
            order__created_at__date__lte=end,
        )
        .values('product__id', 'product__name',
                'product__rate', 'product__mrp', 'product__stock')
        .annotate(
            total_qty     = Sum('quantity'),
            total_revenue = Sum(F('quantity') * F('product__rate')),
            order_count   = Count('order', distinct=True),
        )
        .order_by('-total_qty')
    )

    # Stock status
    out_of_stock  = Product.objects.filter(stock=0)
    low_stock     = Product.objects.filter(stock__gt=0, stock__lte=LOW_STOCK)
    healthy_stock = Product.objects.filter(stock__gt=LOW_STOCK)

    # Summary numbers
    total_products     = Product.objects.count()
    total_sold_qty     = best_selling.aggregate(t=Sum('total_qty'))['t'] or 0
    total_sold_rev     = best_selling.aggregate(t=Sum('total_revenue'))['t'] or 0
    out_of_stock_count = out_of_stock.count()

    # Top 8 for charts
    top8         = list(best_selling[:8])
    chart_labels = [p['product__name']             for p in top8]
    chart_qty    = [p['total_qty']                 for p in top8]
    chart_rev    = [float(p['total_revenue'] or 0) for p in top8]

    all_products = Product.objects.all().order_by('stock')

    return render(request, 'reports/product_report.html', {
        'period':             period,
        'label':              label,
        'start':              start,
        'end':                end,
        'best_selling':       best_selling,
        'out_of_stock':       out_of_stock,
        'low_stock':          low_stock,
        'healthy_stock':      healthy_stock,
        'total_products':     total_products,
        'total_sold_qty':     total_sold_qty,
        'total_sold_rev':     total_sold_rev,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count':    low_stock.count(),
        'chart_labels':       chart_labels,
        'chart_qty':          chart_qty,
        'chart_rev':          chart_rev,
        'all_products':       all_products,
        'LOW_STOCK':          LOW_STOCK,
    })