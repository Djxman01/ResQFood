from django.urls import path
from .views import mp_start, mp_webhook, mp_mock_checkout, mp_mock_approve, payment_status

urlpatterns = [
    path('mp/start/<int:order_id>/', mp_start, name='mp_start'),
    path('mp/mock/<int:order_id>/', mp_mock_checkout, name='mp_mock'),
    path('mp/mock/<int:order_id>/approve/', mp_mock_approve, name='mp_mock_approve'),
    path('status/<int:order_id>/', payment_status, name='payment_status'),
]

# Webhook is mounted at project level as /webhooks/mercadopago/
