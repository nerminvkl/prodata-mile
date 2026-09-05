from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.http import FileResponse, Http404
import os

def serve_media(request, path):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(open(full_path, 'rb'))
    raise Http404

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("pages.urls")),
    path("", include("shop.urls")),
    re_path(r'^media/(?P<path>.*)$', serve_media),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns