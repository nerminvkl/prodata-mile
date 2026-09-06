from django.contrib import admin
from django.utils.text import slugify
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Category, Product, BlogPost, Partner, HeroSlide, Order, OrderItem


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='Grupa artikala',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='label')
    )
    name = fields.Field(column_name='Naziv artikla', attribute='name')
    price = fields.Field(column_name='MPC - KM', attribute='price')

    class Meta:
        model = Product
        fields = ('name', 'category', 'price')
        import_id_fields = ['name']
        skip_unchanged = True

    def before_import_row(self, row, **kwargs):
        cat_name = row.get('Grupa artikala', '')
        if cat_name:
            Category.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={'label': cat_name, 'order': 10}
            )

    def before_save_instance(self, instance, row, **kwargs):
        if not instance.slug:
            base = slugify(instance.name)
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            instance.slug = slug


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["label", "slug", "order"]
    prepopulated_fields = {"slug": ("label",)}
    search_fields = ["label"]
    ordering = ["order"]


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin, ModelAdmin):
    resource_classes = [ProductResource]
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