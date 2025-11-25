from datetime import timedelta
from random import randint, choice

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify

from marketplace.models import Partner, Pack

# Comercios demo (sin acentos para evitar problemas de codificación)
NAMES = [
    ("Verduleria La Hoja", "verduleria"),
    ("Panaderia Trigo Fino", "panaderia"),
    ("Cafe & Deli Centro", "cafe"),
    ("Carniceria El Corte", "carniceria"),
    ("Heladeria Polar", "heladeria"),
    ("Supermercado AhorraMas", "supermercado"),
    ("Almacen Dona Rosa", "almacen"),
    ("Pescaderia Puerto", "pescaderia"),
    ("Dietetica Natural", "dietetica"),
    ("Fabrica de Pastas Nero", "pastas"),
]

# Títulos de packs sugeridos por categoría para que se vean más cercanos a la foto
PACK_VARIANTS = {
    "verduleria": [
        "Bolsa de verduras de estacion",
        "Mix fresco para sopas y salteados",
        "Combo verde: hojas y raices",
    ],
    "panaderia": [
        "Pan de masa madre y facturas",
        "Pack dulce: medialunas y budin",
        "Panaderia variada de la tarde",
    ],
    "cafe": [
        "Brunch para dos con cafe",
        "Box dulce: torta y cookies",
        "Sandwich gourmet con bebida",
    ],
    "carniceria": [
        "Cortes seleccionados para la semana",
        "Mix de milanesas y carne picada",
        "Parrillero: chorizos y tira",
    ],
    "heladeria": [
        "Helados artesanales 1Kg",
        "Torta helada variada",
        "Combo medio kilo y toppings",
    ],
    "supermercado": [
        "Canasta ahorro: secos y limpieza",
        "Pack desayuno y snacks",
        "Basicos de despensa y lacteos",
    ],
    "almacen": [
        "Almacen variado: fideos y salsas",
        "Combo merienda: galletas y te",
        "Desayuno completo para la semana",
    ],
    "pescaderia": [
        "Filetes de pescado blanco",
        "Mix marino para paella",
        "Pescados del dia con limon",
    ],
    "dietetica": [
        "Mix saludable: frutos secos y semillas",
        "Desayuno fit: granola y miel",
        "Pack veggie con legumbres",
    ],
    "pastas": [
        "Pastas frescas surtidas",
        "Ravioles con salsa casera",
        "Nyoquis con queso rallado",
    ],
}


def ensure_demo_packs(min_count: int = 40):
    """Garantiza que existan al menos `min_count` packs demo."""
    # Refresca nombres de packs demo antiguos para que se vean más descriptivos
    for pack in Pack.objects.filter(titulo__istartswith="Pack demo"):
        cat = getattr(getattr(pack, "partner", None), "categoria", "")
        pack.titulo = choice(PACK_VARIANTS.get(cat, ["Pack variado para llevar"]))
        pack.save(update_fields=["titulo"])

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

        categoria = getattr(partner, "categoria", "")
        titulo = choice(PACK_VARIANTS.get(categoria, ["Pack variado para llevar"]))

        Pack.objects.create(
            partner=partner,
            titulo=titulo,
            etiqueta=choice(etiquetas),
            precio_original=precio_original,
            precio_oferta=precio_oferta,
            stock=stock,
            pickup_start=pickup_start,
            pickup_end=pickup_end,
        )
