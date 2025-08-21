# resqfood/urls.py
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
]
