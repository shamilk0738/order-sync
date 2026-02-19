from django.urls import path
from . import views

urlpatterns = [
    path('',              views.store_list,   name='store_front'),
    path('<int:id>/',     views.store_detail, name='store_detail'),
    # NEW: click store name → orders by date
    path('<int:id>/orders/', views.store_orders, name='store_orders'),
]