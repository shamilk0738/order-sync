from django.urls import path
from . import views

urlpatterns = [
     path('stores/', views.store_list, name='store_front'),
     path('store/<int:id>/', views.store_detail, name='store_detail'),

]
