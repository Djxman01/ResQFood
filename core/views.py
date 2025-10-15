from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from marketplace.models import Partner, Pack

def home(request):
    merchants = Partner.with_active_packs().order_by('nombre')
    # Ensure merchants have a slug to avoid '/merchant/None/' links
    for m in merchants:
        if not m.slug:
            base = slugify(m.nombre) or f"partner-{m.id}"
            cand = base
            i = 1
            while Partner.objects.filter(slug=cand).exclude(id=m.id).exists():
                i += 1
                cand = f"{base}-{i}"
            m.slug = cand
            m.save(update_fields=["slug"])
    return render(request, "core/home.html", {"merchants": merchants})
