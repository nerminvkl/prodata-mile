from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    label = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon_svg = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Kategorija"
        verbose_name_plural = "Kategorije"

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Proizvod"
        verbose_name_plural = "Proizvodi"

    def __str__(self):
        return self.name

    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price

    @property
    def discount_percent(self):
        if self.is_on_sale:
            return round((1 - self.sale_price / self.price) * 100)
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to="blog/", blank=True)
    date = models.DateField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Vijest"
        verbose_name_plural = "Vijesti"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Partner(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="partners/")
    url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Partner"
        verbose_name_plural = "Partneri"

    def __str__(self):
        return self.name


class HeroSlide(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="hero/", blank=True)
    btn_primary_text = models.CharField(max_length=50, blank=True)
    btn_primary_url = models.CharField(max_length=200, blank=True)
    btn_secondary_text = models.CharField(max_length=50, blank=True)
    btn_secondary_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Uvodni dio"
        verbose_name_plural = "Uvodni dio"

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ('nova', 'Nova'),
        ('u_obradi', 'U obradi'),
        ('isporucena', 'Isporučena'),
        ('otkazana', 'Otkazana'),
    ]
    ime = models.CharField(max_length=100)
    prezime = models.CharField(max_length=100)
    telefon = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    adresa = models.TextField()
    napomena = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='nova')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Narudžba"
        verbose_name_plural = "Narudžbe"

    def __str__(self):
        return f"Narudžba #{self.pk} — {self.ime} {self.prezime}"

    def ukupno(self):
        return sum(item.ukupno() for item in self.stavke.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='stavke')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    naziv = models.CharField(max_length=200)
    cijena = models.DecimalField(max_digits=10, decimal_places=2)
    kolicina = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Stavka narudžbe"
        verbose_name_plural = "Stavke narudžbe"

    def ukupno(self):
        return self.cijena * self.kolicina