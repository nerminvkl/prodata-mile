from django.shortcuts import render, get_object_or_404
from .models import Category, Product, BlogPost, Partner
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import logging
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)



def home(request):
    context = {
        "categories": Category.objects.all(),
        "recently_added": Product.objects.filter(is_active=True)[:8],
        "featured": Product.objects.filter(is_active=True, is_featured=True)[:8],
        "on_sale": Product.objects.filter(is_active=True, sale_price__isnull=False)[:8],
        "blog_posts": BlogPost.objects.filter(is_published=True)[:3],
        "partners": Partner.objects.all(),
    }
    return render(request, "shop/home.html", context)

def catalog(request):
    products = Product.objects.filter(is_active=True)
    category_slug = request.GET.get("category")
    brand = request.GET.get("brand")

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand:
        products = products.filter(brand=brand)

    brands = Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct().exclude(brand='').order_by('brand')

    paginator = Paginator(products, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "active_category": category_slug,
        "brands": brands,
        "active_brand": brand,
    }
    return render(request, "shop/catalog.html", context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "shop/product_detail.html", {"product": product})

def pos(request):
    products = Product.objects.filter(is_active=True, category__slug="pos-kase")
    return render(request, "shop/pos.html", {"products": products})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, "shop/blog_detail.html", {"post": post})

def servis(request):
    return render(request, "shop/servis.html", {})

def kontakt(request):
    if request.method == 'POST':
        # Honeypot anti-spam
        if request.POST.get('website'):
            logger.warning('Honeypot okinut: %r', request.POST.get('website'))
            return redirect('kontakt')

        name = request.POST.get('name', '').strip()
        contact = request.POST.get('contact', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not contact or not message:
            messages.error(request, 'Molimo popunite sva polja.')
            return redirect('kontakt')

        email = EmailMessage(
            subject=f'Upit sa web stranice — {name}',
            body=f'Ime: {name}\nKontakt: {contact}\n\nPoruka:\n{message}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['nermin.vkl@gmail.com'],
            reply_to=[contact] if '@' in contact else None,
        )
        try:
            email.send(fail_silently=False)
        except Exception:
            logger.exception('Slanje kontakt maila nije uspjelo')
            messages.error(request, 'Poruka nije poslana. Pokušajte ponovo ili nas pozovite.')
            return redirect('kontakt')

        messages.success(request, 'Vaš upit je uspješno poslan!')
        return redirect('kontakt')

    return render(request, 'shop/kontakt.html', {})

def cart(request):
    return render(request, "shop/cart.html", {})

from .models import Category, Product, BlogPost, Partner, HeroSlide, Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

def cart(request):
    cart = request.session.get('cart', {})
    items = []
    ukupno = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=pid)
            cijena = p.sale_price if p.is_on_sale else p.price
            items.append({'product': p, 'kolicina': qty, 'cijena': cijena, 'subtotal': cijena * qty})
            ukupno += cijena * qty
        except Product.DoesNotExist:
            pass
    return render(request, 'shop/cart.html', {'items': items, 'ukupno': ukupno})

def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    messages.success(request, 'Proizvod dodan u korpu.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    items = []
    ukupno = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=pid)
            cijena = p.sale_price if p.is_on_sale else p.price
            items.append({'product': p, 'kolicina': qty, 'cijena': cijena, 'subtotal': cijena * qty})
            ukupno += cijena * qty
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        order = Order.objects.create(
            ime=request.POST.get('ime'),
            prezime=request.POST.get('prezime'),
            telefon=request.POST.get('telefon'),
            email=request.POST.get('email', ''),
            adresa=request.POST.get('adresa'),
            napomena=request.POST.get('napomena', ''),
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                naziv=item['product'].name,
                cijena=item['cijena'],
                kolicina=item['kolicina'],
            )

        stavke_txt = '\n'.join([
            f"- {oi.naziv} x{oi.kolicina} = {oi.cijena * oi.kolicina} KM"
            for oi in order.stavke.all()
        ])

        # Email adminu
        send_mail(
            subject=f'🛒 Nova narudžba #{order.pk} — {order.ime} {order.prezime}',
            message=f'''Nova narudžba primljena!

Kupac: {order.ime} {order.prezime}
Telefon: {order.telefon}
Email: {order.email}
Adresa: {order.adresa}
Napomena: {order.napomena}

Stavke:
{stavke_txt}

Ukupno: {order.ukupno()} KM

Admin: https://prodata.ba/admin/shop/order/{order.pk}/change/
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['prodata.d.o.o@gmail.com'],
            fail_silently=True,
        )

        # Email kupcu (ako je unio email)
        if order.email:
            send_mail(
                subject=f'Potvrda narudžbe #{order.pk} — ProData d.o.o.',
                message=f'''Poštovani {order.ime} {order.prezime},

Hvala na narudžbi! Primili smo vašu narudžbu i kontaktiraćemo vas u najkraćem roku.

Vaša narudžba #{order.pk}:
{stavke_txt}

Ukupno: {order.ukupno()} KM
Adresa dostave: {order.adresa}
{f"Napomena: {order.napomena}" if order.napomena else ""}

Za pitanja nas kontaktirajte:
Tel: +387 37 770-079
Mobitel: +387 61 231-363
Email: prodata.d.o.o@gmail.com

ProData d.o.o.
Ulica Mahmuta Zulića 11, 77 230 Velika Kladuša
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=True,
            )

        request.session['cart'] = {}
        return redirect('order_success')

    return render(request, 'shop/checkout.html', {'items': items, 'ukupno': ukupno})


def order_success(request):
    return render(request, 'shop/order_success.html', {})

from django.http import JsonResponse

def search_ajax(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    products = Product.objects.filter(is_active=True).filter(
    Q(name__icontains=q) | Q(brand__icontains=q)
    )[:8]
    results = []
    for p in products:
        results.append({
            'name': p.name,
            'price': str(p.sale_price if p.is_on_sale else p.price),
            'url': f'/katalog/{p.slug}/',
            'image': p.image.url if p.image else '',
            'category': str(p.category) if p.category else '',
            'brand': p.brand,
        })
    return JsonResponse({'results': results})