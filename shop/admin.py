from django.contrib import admin
from .models import Category, Product, BlogPost, Partner, HeroSlide, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["label", "slug", "order"]
    prepopulated_fields = {"slug": ("label",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "sale_price", "is_featured", "is_active"]
    list_filter = ["category", "is_featured", "is_active"]
    prepopulated_fields = {"slug": ("name",)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "is_published"]
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["title", "order", "is_active"]
    list_editable = ["order", "is_active"]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['naziv', 'cijena', 'kolicina']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'ime', 'prezime', 'telefon', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    inlines = [OrderItemInline]