# resqfood/urls.py
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),          # <- home en "/"

    # FRONTEND (templates)
    path("packs/", include("packs.urls")),   # /packs/ -> HTML

    # API (todo lo de DRF va debajo de /api/)
    path("api/", include("api.urls")),       # /api/packs/ -> JSON
    path("api/payments/", include("payments.urls")),

    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("accounts.urls")),   
    path('', include('marketplace.urls')),
    path("webhooks/mercadopago/", include("payments.urls_webhooks")),

    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
