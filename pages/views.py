from django.views.generic import TemplateView
from shop.models import Category, Product, BlogPost, Partner, HeroSlide


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["recently_added"] = Product.objects.filter(is_active=True)[:5]
        ctx["featured"] = Product.objects.filter(is_active=True, is_featured=True)[:5]
        ctx["on_sale"] = Product.objects.filter(is_active=True, sale_price__isnull=False)[:5]
        ctx["blog_posts"] = BlogPost.objects.filter(is_published=True)[:3]
        ctx["partners"] = Partner.objects.all()
        ctx["hero_slides"] = HeroSlide.objects.filter(is_active=True)
        ctx["partner_logos_default"] = Partner.objects.all()
        return ctx


class AboutPageView(TemplateView):
    template_name = "pages/about.html"
