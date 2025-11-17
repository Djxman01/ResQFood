from datetime import timedelta
from random import randint, choice

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

from marketplace.models import Partner, Pack

NAMES = [
    ("Verdulería La Hoja", "verduleria"),
    ("Panadería Trigo Fino", "panaderia"),
    ("Café & Deli Centro", "cafe"),
    ("Carnicería El Corte", "carniceria"),
    ("Heladería Polar", "heladeria"),
    ("Supermercado AhorraMás", "supermercado"),
    ("Almacén Doña Rosa", "almacen"),
    ("Pescadería Puerto", "pescaderia"),
    ("Dietética Natural", "dietetica"),
    ("Fábrica de Pastas Nero", "pastas"),
]


def ensure_demo_packs(min_count: int = 40):
    """Garantiza que existan al menos `min_count` packs demo."""
    existing = Pack.objects.count()
    if existing >= min_count:
        return

    user_model = get_user_model()
    owner, _ = user_model.objects.get_or_create(
        username="demo_owner",
        defaults={"email": "demo@example.com"},
    )

    partners = list(Partner.objects.all())
    if not partners:
        for name, categoria in NAMES:
            partners.append(
                Partner.objects.create(
                    owner=owner,
                    nombre=name,
                    categoria=categoria,
                    direccion="Av. Demo 123",
                    slug=slugify(name)[:140],
                )
            )

    if not partners:
        return

    needed = min_count - existing
    now = timezone.now()
    etiquetas = ["excedente", "por_vencer"]

    for i in range(needed):
        partner = partners[i % len(partners)]
        precio_original = float(randint(1800, 6200))
        descuento = choice([10, 15, 20, 25])
        precio_oferta = round(precio_original * (1 - descuento / 100.0), 2)
        stock = randint(3, 12)
        pickup_start = now + timedelta(hours=randint(-2, 1))
        pickup_end = now + timedelta(hours=randint(4, 10))

        Pack.objects.create(
            partner=partner,
            titulo=f"Pack demo #{timezone.now().strftime('%H%M%S')}-{i + 1}",
            etiqueta=choice(etiquetas),
            precio_original=precio_original,
            precio_oferta=precio_oferta,
            stock=stock,
            pickup_start=pickup_start,
            pickup_end=pickup_end,
        )

