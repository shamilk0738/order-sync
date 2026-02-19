from django.urls import path
from . import views

urlpatterns = [
    path('sales/',             views.sales_report,             name='sales_report'),
    path('staff-performance/', views.staff_performance_report, name='staff_performance_report'),
    path('stores/',            views.store_report,             name='store_report'),
    path('products/',          views.product_report,           name='product_report'),
]