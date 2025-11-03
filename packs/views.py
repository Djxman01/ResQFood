from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import F, Count
from marketplace.models import Pack, Order
from payments.models import Payment

def pack_list(request):
    now = timezone.now()
    qs = Pack.objects.select_related("partner").all()

    oferta = request.GET.get("oferta") == "1"
    stock = request.GET.get("stock") == "1"
    abierto = request.GET.get("abierto") == "1"

    if oferta:
        qs = qs.filter(precio_oferta__lt=F("precio_original"))
    if stock:
        qs = qs.filter(stock__gt=0)
    if abierto:
        qs = qs.filter(pickup_start__lte=now, pickup_end__gte=now)

    orden = (request.GET.get("orden") or "nuevo").strip()
    if orden == "precio-asc":
        qs = qs.order_by(
            F("precio_oferta").asc(nulls_last=True),
            F("precio_original").asc(nulls_last=True),
            "-creado_at",
        )
    elif orden == "precio-desc":
        qs = qs.order_by(
            F("precio_oferta").desc(nulls_last=True),
            F("precio_original").desc(nulls_last=True),
            "-creado_at",
        )
    elif orden == "mas-comprado":
        try:
            qs = qs.annotate(n=Count("orders")).order_by("-n", "-creado_at")
        except Exception:
            qs = qs.order_by("-creado_at")
    else:
        qs = qs.order_by("-creado_at")

    page = Paginator(qs, 24).get_page(request.GET.get("page"))

    return render(
        request,
        "marketplace/packs_list.html",
        {
            "page": page,
            "f_oferta": oferta,
            "f_stock": stock,
            "f_abierto": abierto,
            "orden": orden,
        },
    )

def pack_detail(request, pk):
    pack = get_object_or_404(Pack.objects.select_related("partner"), pk=pk)
    now = timezone.now()

    pending_order = None
    if request.user.is_authenticated:
        pending_order = (
            Order.objects.filter(user=request.user, pack=pack, estado="pendiente")
            .order_by("-creado_at")
            .first()
        )

    last_payment = None
    if pending_order:
        last_payment = Payment.objects.filter(order=pending_order).order_by("-created_at").first()

    related = (
        Pack.objects.filter(partner=pack.partner).exclude(id=pack.id).order_by("-creado_at")[:8]
    )

    price_show = pack.precio_oferta or pack.precio_original

    ctx = {
        "pack": pack,
        "pending_order": pending_order,
        "last_payment": last_payment,
        "related": related,
        "now": now,
        "price_show": price_show,
        "meta_title": f"{pack.titulo} — {pack.partner.nombre} | ResQFood",
        "meta_desc": f"{pack.titulo} en {pack.partner.nombre}. Retiro {pack.pickup_start:%d/%m %H:%M}–{pack.pickup_end:%H:%M}. Stock {pack.stock}.",
    }
    return render(request, "marketplace/pack_detail.html", ctx)
