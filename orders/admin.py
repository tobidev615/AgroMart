from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "produce", "quantity", "added_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "user__username")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "subtotal")

# Register your models here.
