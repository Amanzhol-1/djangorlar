from django.contrib import admin
from .models import Restaurant, Category, Option, MenuItem, ItemCategory, ItemOption


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class ItemCategoryInline(admin.TabularInline):
    model = ItemCategory
    extra = 0


class ItemOptionInline(admin.TabularInline):
    model = ItemOption
    extra = 0


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "base_price", "is_available", "is_active", "created_at", "updated_at")
    list_filter = ("restaurant", "is_available", "is_active")
    search_fields = ("name", "restaurant__name")
    inlines = [ItemCategoryInline, ItemOptionInline]

admin.site.register(ItemCategory)
admin.site.register(ItemOption)