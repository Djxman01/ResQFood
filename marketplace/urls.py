# marketplace/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartnerViewSet, PackViewSet, OrderViewSet, MisReservasView,OrderDetailView, order_qr_view, partner_redeem_page, CartViewSet, cart_page, merchant_detail


router = DefaultRouter()
router.register(r'partners', PartnerViewSet)
router.register(r'packs',    PackViewSet, basename='pack')
router.register(r'orders',   OrderViewSet)
router.register(r'cart',     CartViewSet, basename='cart')

urlpatterns = [
    path('api/', include(router.urls)),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail_public'),
    path('cart/', cart_page, name='cart'),
    path('merchant/<slug:slug>/', merchant_detail, name='merchant_detail'),
    path('mis-reservas/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),   
    path('mis-reservas/<int:pk>/qr.png', order_qr_view, name='order_qr'),   
    path('partner/redeem/', partner_redeem_page, name='partner_redeem'),
]
