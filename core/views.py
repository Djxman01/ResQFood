from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Count, F, Q
from marketplace.models import Partner, Pack

def home(request):
    # Static categories (can be wired to real filters later)
    categories = [
        {"slug": "restaurantes", "title": "Restaurantes", "icon": "🍔"},
        {"slug": "super", "title": "Súper", "icon": "🛒"},
        {"slug": "kioscos", "title": "Kioscos", "icon": "🥤"},
        {"slug": "helados", "title": "Helados", "icon": "🍨"},
        {"slug": "cafes", "title": "Cafés", "icon": "☕"},
        {"slug": "verdulerias", "title": "Verdulerías", "icon": "🥬"},
        {"slug": "carnicerias", "title": "Carnicerías", "icon": "🥩"},
        {"slug": "fruterias", "title": "Fruterías", "icon": "🍎"},
    ]

    now = timezone.now()
    active_filter = Q(stock__gt=0, pickup_end__gte=now)

    # Newest: latest created and active
    newest = (
        Pack.objects.filter(active_filter)
        .order_by("-creado_at")[:12]
    )

    # Most bought: by number of orders
    most_bought = (
        Pack.objects.filter(active_filter)
        .annotate(n=Count("orders"))
        .order_by("-n", "-creado_at")[:12]
    )

    # Offers: oferta < original
    offers = (
        Pack.objects.filter(active_filter)
        .filter(precio_oferta__isnull=False)
        .filter(precio_oferta__lt=F("precio_original"))
        .order_by("precio_oferta")[:12]
    )

    ctx = {
        "categories": categories,
        "newest": newest,
        "most_bought": most_bought,
        "offers": offers,
    }
    return render(request, "core/home_enriched.html", ctx)
