from django.urls import path
from .views import staff_index

urlpatterns = [
    path('', staff_index, name='staff_index'),
]
