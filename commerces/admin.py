from django.contrib import admin
from .models import Address, Order, OrderItem, OrderItemOption, PromoCode, OrderPromo, Payment


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "city", "street", "house", "is_primary", "created_at")
    list_filter = ("city", "is_primary")
    search_fields = ("user__username", "label", "street", "house")


class OrderItemOptionInline(admin.TabularInline):
    model = OrderItemOption
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    show_change_link = True


class OrderPromoInline(admin.TabularInline):
    model = OrderPromo
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant", "address", "status", "subtotal", "discount_total", "total", "created_at")
    list_filter = ("status", "restaurant")
    search_fields = ("id", "user__username", "restaurant__name")
    inlines = [OrderItemInline, OrderPromoInline, PaymentInline]

admin.site.register(OrderItem)
admin.site.register(OrderItemOption)
admin.site.register(PromoCode)
admin.site.register(OrderPromo)
admin.site.register(Payment)