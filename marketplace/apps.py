from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'

    def ready(self):
        # Ensure additional models modules are imported so Django registers them
        from . import models_cart  # noqa: F401
