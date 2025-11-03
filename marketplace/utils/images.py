import hashlib
import os
from pathlib import Path
from django.templatetags.static import static
from django.conf import settings

CATEGORY_DIR_MAP = {
    # Plural and singular aliases
    "restaurantes": "restaurantes",
    "restaurante": "restaurantes",
    "supermercados": "supermercados",
    "supermercado": "supermercados",
    "helados": "helados",
    "heladeria": "helados",
    "cafes": "cafes",
    "cafe": "cafes",
    "carniceria": "carniceria",
    "verduleria": "verduleria",
    "panaderia": "panaderia",
    "kiosco": "supermercados",
    # Extra real-world categories used in demo data
    "dietetica": "verduleria",
    "almacen": "supermercados",
    "pescaderia": "carniceria",
    "pastas": "restaurantes",
    "otros": "restaurantes",
}

def _hash_to_index(text, max_n):
    h = hashlib.md5((text or "x").encode("utf-8")).hexdigest()
    return (int(h[:8], 16) % max_n) if max_n > 0 else 0

def _static_exists(rel_path: str) -> bool:
    try:
        root = Path(getattr(settings, "BASE_DIR", os.getcwd())) / "static"
        return (root / Path(rel_path)).exists()
    except Exception:
        return False


def stock_image_url(category_slug, key_text=""):
    base = getattr(settings, "STOCK_IMAGE_ROOT", "img/stock")
    slug = (category_slug or "").lower()
    folder = CATEGORY_DIR_MAP.get(slug, slug or "otros")
    count_guess = 10
    idx = _hash_to_index(key_text or folder, count_guess) + 1

    exts = ("jpg", "jpeg", "png", "webp")

    # 1) Try hashed index with common extensions
    for ext in exts:
        candidate = f"{base}/{folder}/{idx}.{ext}"
        if _static_exists(candidate):
            return static(candidate)

    # 2) Fallback: scan 1..count_guess for any available ext
    for j in range(1, count_guess + 1):
        for ext in exts:
            candidate = f"{base}/{folder}/{j}.{ext}"
            if _static_exists(candidate):
                return static(candidate)

    # 2b) No numeric files: pick any file with a supported extension from the folder
    try:
        root = Path(getattr(settings, "BASE_DIR", os.getcwd())) / "static" / base / folder
        if root.exists() and root.is_dir():
            for ext in exts:
                files = sorted(root.glob(f"*.{ext}"))
                if files:
                    # build rel path from static root
                    rel = f"{base}/{folder}/{files[0].name}"
                    return static(rel)
    except Exception:
        pass

    # 3) Ultimate fallback: placeholder
    return static("img/placeholder-pack.svg")
