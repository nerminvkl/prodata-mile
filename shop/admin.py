from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Category, Product, BlogPost, Partner, HeroSlide, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["label", "slug", "order"]
    prepopulated_fields = {"slug": ("label",)}
    search_fields = ["label"]
    ordering = ["order"]


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["name", "category", "price", "sale_price", "show_discount", "is_featured", "is_active"]
    list_filter = ["category", "is_featured", "is_active"]
    list_filter_submit = True
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]
    list_editable = ["is_featured", "is_active"]
    readonly_fields = ["created_at", "updated_at"]

    @display(description="Popust", label=True)
    def show_discount(self, obj):
        if obj.discount_percent:
            return f"-{obj.discount_percent}%"
        return ""


@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ["title", "date", "is_published"]
    list_editable = ["is_published"]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ["title"]
    readonly_fields = ["date"]


@admin.register(Partner)
class PartnerAdmin(ModelAdmin):
    list_display = ["name", "order"]
    list_editable = ["order"]
    search_fields = ["name"]


@admin.register(HeroSlide)
class HeroSlideAdmin(ModelAdmin):
    list_display = ["title", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["title"]


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["naziv", "cijena", "kolicina"]
    tab = True


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["id", "ime", "prezime", "telefon", "show_status", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    readonly_fields = ["created_at"]
    inlines = [OrderItemInline]
    search_fields = ["ime", "prezime", "telefon", "email"]

    @display(description="Status", label={
        "nova": "info",
        "u_obradi": "warning",
        "isporucena": "success",
        "otkazana": "danger",
    })
    def show_status(self, obj):
        return obj.status