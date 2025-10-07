# marketplace/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, PackViewSet, OrderViewSet, MisReservasView

router = DefaultRouter()
router.register(r'partners', PartnerViewSet)
router.register(r'packs',    PackViewSet, basename='pack')
router.register(r'orders',   OrderViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
]
