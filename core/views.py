from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Count, F, Q
from marketplace.models import Partner, Pack
from marketplace.services.filters import apply_pack_filters, ui_filter_state

def home(request):
    base = Pack.objects.all()
    newest = apply_pack_filters(base, request.GET)[:24]

    params = request.GET.copy()
    params_mb = params.copy()
    params_mb["orden"] = params_mb.get("orden") or "mas-comprado"
    most_bought = apply_pack_filters(base, params_mb)[:24]

    params_of = params.copy()
    params_of["oferta"] = "1"
    offers = apply_pack_filters(base, params_of)[:24]

    ctx = {
        "filter_state": ui_filter_state(request.GET),
        "newest": newest,
        "most_bought": most_bought,
        "offers": offers,
    }
    return render(request, "core/home_enriched.html", ctx)
