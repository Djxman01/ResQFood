try:
    import mercadopago  # type: ignore
except Exception:  # pragma: no cover
    mercadopago = None  # lazy-loaded / mocked in tests

from django.conf import settings


def create_mp_preference(order):
    """
    Create a Mercado Pago Preference for an order.
    Returns dict: {
      'preference_id': str,
      'init_point': str | None,
      'sandbox_init_point': str | None,
    }
    """
    if mercadopago is None:
        raise RuntimeError("MercadoPago SDK not installed")

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    # Since this app models one pack per order, build a single line item
    p = order.pack
    items = [{
        "title": getattr(p, "titulo", "Item"),
        "quantity": 1,
        "unit_price": float(getattr(order, "precio_pagado", getattr(p, "precio_oferta", 0))),
        "currency_id": "ARS",
    }]

    back_urls = {
        "success": settings.MP_BACK_URL_SUCCESS,
        "pending": settings.MP_BACK_URL_PENDING,
        "failure": settings.MP_BACK_URL_FAILURE,
    }

    pref_body = {
        "items": items,
        "external_reference": str(order.id),
        "notification_url": settings.MP_NOTIFICATION_URL,
        "back_urls": back_urls,
    }

    # Only add auto_return if success URL exists
    if settings.MP_BACK_URL_SUCCESS:
        pref_body["auto_return"] = "approved"

    resp = sdk.preference().create(pref_body)
    data = resp.get("response", {}) if isinstance(resp, dict) else {}
    return {
        "preference_id": data.get("id"),
        "init_point": data.get("init_point"),
        "sandbox_init_point": data.get("sandbox_init_point"),
    }


  