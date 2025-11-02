from django.db import models
from django.conf import settings
from django.utils import timezone


class Payment(models.Model):
    PROVIDERS = (
        ("mp", "MercadoPago"),
    )
    order = models.ForeignKey('marketplace.Order', on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=16, choices=PROVIDERS)
    preference_id = models.CharField(max_length=120, blank=True)
    # New fields for real provider integration
    payment_id = models.CharField(max_length=64, null=True, blank=True)
    request_id = models.CharField(max_length=128, null=True, blank=True, unique=True)
    raw_event = models.JSONField(null=True, blank=True)

    STATUS_CHOICES = [
        ("pending", "pending"),
        ("approved", "approved"),
        ("rejected", "rejected"),
        ("cancelled", "cancelled"),
        ("refunded", "refunded"),
        ("chargeback", "chargeback"),
        ("in_mediation", "in_mediation"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider}:{self.status} for {self.order_id}"

    @staticmethod
    def last_for_order(order):
        return Payment.objects.filter(order=order).order_by('-created_at').first()

    def apply_status(self, new_status: str):
        terminal_priority = {
            "pending": 1, "in_mediation": 2, "rejected": 3, "cancelled": 3,
            "approved": 4, "refunded": 5, "chargeback": 6,
        }
        if terminal_priority.get(new_status, 0) < terminal_priority.get(self.status, 0):
            return False
        self.status = new_status
        if new_status == "approved" and not self.paid_at:
            self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])
        return True

    def mark_approved_manual(self):
        """
        Marca el pago como aprobado de manera idempotente y actualiza la orden.
        Útil para efectivo/transferencia o ajustes manuales.
        """
        changed = self.apply_status("approved")
        # Idempotente sobre la orden
        try:
            if self.order:
                self.order.mark_paid()
        except Exception:
            pass
        return changed


class WebhookLog(models.Model):
    request_id = models.CharField(max_length=128, unique=True)
    headers = models.JSONField()
    body = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
