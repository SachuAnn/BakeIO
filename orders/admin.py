from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'bakery', 'status', 'created_at')
    list_filter = ('status', 'bakery')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
