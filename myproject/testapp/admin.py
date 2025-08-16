from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'status', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    list_editable = ['status', 'is_featured']
    prepopulated_fields = {}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_amount', 'order_date', 'is_paid']
    search_fields = ['user__username', 'user__email']
    list_filter = ['is_paid', 'order_date']
    inlines = [OrderItemInline]
    readonly_fields = ['order_date']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price_at_time']
    search_fields = ['product__name', 'order__id']
    list_filter = ['order__order_date']
