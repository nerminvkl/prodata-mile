from django.contrib import admin
from django.utils.text import slugify
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Category, Product, BlogPost, Partner, HeroSlide, Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings


class ProductResource(resources.ModelResource):
    category = fields.Field(
        column_name='Grupa artikala',
        attribute='category',
        widget=ForeignKeyWidget(Category, field='label')
    )
    name = fields.Field(column_name='Naziv artikla', attribute='name')
    price = fields.Field(column_name='MPC - KM', attribute='price')
    brand = fields.Field(column_name='Brand', attribute='brand')

    class Meta:
        model = Product
        fields = ('name', 'category', 'price', 'brand')
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
        model_code = row.get('Model', '')
        naziv = row.get('Naziv artikla', '')
        if not instance.slug:
            base = slugify(f"{naziv}-{model_code}" if model_code else naziv)
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
    list_display = ["name", "brand", "category", "price", "sale_price", "show_discount", "is_featured", "is_active"]
    list_filter = ["category", "brand", "is_featured", "is_active"]
    list_filter_submit = True
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "brand"]
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
    list_display = ["id", "ime", "prezime", "telefon", "show_status", "ukupno_display", "created_at"]
    list_filter = ["status"]
    list_filter_submit = True
    readonly_fields = ["created_at"]
    inlines = [OrderItemInline]
    search_fields = ["ime", "prezime", "telefon", "email"]
    actions = ["mark_u_pripremi", "mark_poslano", "mark_isporucena", "mark_otkazana"]

    @display(description="Status", label={
        "nova": "info",
        "u_pripremi": "warning",
        "poslano": "warning",
        "isporucena": "success",
        "otkazana": "danger",
    })
    def show_status(self, obj):
        return obj.get_status_display()

    @display(description="Ukupno")
    def ukupno_display(self, obj):
        return f"{obj.ukupno()} KM"

    def mark_u_pripremi(self, request, queryset):
        queryset.update(status='u_pripremi')
    mark_u_pripremi.short_description = "→ U pripremi"

    def mark_poslano(self, request, queryset):
        queryset.update(status='poslano')
    mark_poslano.short_description = "→ Poslano"

    def mark_isporucena(self, request, queryset):
        queryset.update(status='isporucena')
    mark_isporucena.short_description = "→ Isporučena"

    def mark_otkazana(self, request, queryset):
        queryset.update(status='otkazana')
    mark_otkazana.short_description = "→ Otkazana"

    def send_status_email(self, order, status_display):
        if not order.email:
            return
        
        poruke = {
            'U pripremi': 'Vaša narudžba je primljena i trenutno se priprema za isporuku.',
            'Poslano': 'Vaša narudžba je poslana i uskoro će biti dostavljena na vašu adresu.',
            'Isporučena': 'Vaša narudžba je uspješno isporučena. Hvala na kupovini!',
            'Otkazana': 'Nažalost, vaša narudžba je otkazana. Kontaktirajte nas za više informacija.',
        }

        poruka = poruke.get(status_display, '')
        stavke_txt = '\n'.join([
            f"- {oi.naziv} x{oi.kolicina} = {oi.cijena * oi.kolicina} KM"
            for oi in order.stavke.all()
        ])

        send_mail(
            subject=f'Narudžba #{order.pk} — {status_display}',
            message=f'''Poštovani {order.ime} {order.prezime},

{poruka}

Vaša narudžba #{order.pk}:
{stavke_txt}

Ukupno: {order.ukupno()} KM
Adresa dostave: {order.adresa}

Za pitanja nas kontaktirajte:
Tel: +387 37 770-079
Email: prodata.d.o.o@gmail.com

Hvala što kupujete kod ProData d.o.o.
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )

    def mark_u_pripremi(self, request, queryset):
        queryset.update(status='u_pripremi')
        for order in queryset:
            self.send_status_email(order, 'U pripremi')
    mark_u_pripremi.short_description = "→ U pripremi"

    def mark_poslano(self, request, queryset):
        queryset.update(status='poslano')
        for order in queryset:
            self.send_status_email(order, 'Poslano')
    mark_poslano.short_description = "→ Poslano"

    def mark_isporucena(self, request, queryset):
        queryset.update(status='isporucena')
        for order in queryset:
            self.send_status_email(order, 'Isporučena')
    mark_isporucena.short_description = "→ Isporučena"

    def mark_otkazana(self, request, queryset):
        queryset.update(status='otkazana')
        for order in queryset:
            self.send_status_email(order, 'Otkazana')
    mark_otkazana.short_description = "→ Otkazana"