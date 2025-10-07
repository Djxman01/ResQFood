# resqfood/urls.py
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),          # <- home en "/"

    # FRONTEND (templates)
    path("packs/", include("packs.urls")),   # /packs/ -> HTML

    # API (todo lo de DRF va debajo de /api/)
    path("api/", include("api.urls")),       # /api/packs/ -> JSON

    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),   
    path('', include('marketplace.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)