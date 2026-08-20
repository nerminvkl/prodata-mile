from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("katalog/", views.catalog, name="catalog"),
    path("katalog/<slug:slug>/", views.product_detail, name="product_detail"),
    path("pos/", views.pos, name="pos"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("servis/", views.servis, name="servis"),
    path("kontakt/", views.kontakt, name="kontakt"),
    path("korpa/", views.cart, name="cart"),
    path("korpa/dodaj/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("korpa/ukloni/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("naruci/", views.checkout, name="checkout"),
    path("naruci/uspjesno/", views.order_success, name="order_success"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("search/", views.search_ajax, name="search_ajax"),
]