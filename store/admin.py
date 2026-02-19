from django.contrib import admin
from .models import AdminStore

@admin.register(AdminStore)
class AdminStoreAdmin(admin.ModelAdmin):
    list_display = (
        'store_name',
        'gst_number',
        'phone_number',
        'state',
        'email'
    )