from rest_framework import viewsets, permissions, decorators, response, status, filters
from .models import Partner, Pack, Order
from .serializers import PartnerSerializer, PackSerializer, OrderSerializer
from .permissions import IsPartner
from django_filters.rest_framework import DjangoFilterBackend

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

class PackViewSet(viewsets.ModelViewSet):
    queryset = Pack.objects.select_related("partner").all().order_by("-creado_at")
    serializer_class = PackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["etiqueta", "partner"]
    ordering_fields = ["creado_at", "precio_oferta"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "etiqueta", "partner__nombre"]   # para ?search=
    ordering_fields = ["precio_oferta", "creado_at"]            # para ?ordering=
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user", "pack", "pack__partner").all().order_by("-creado_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario ve sus propias órdenes
        return super().get_queryset().filter(user=self.request.user)

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsPartner])
    def redeem(self, request, pk=None):
        """
        Partner marca una orden como RETIRADA.
        Validaciones:
        - El usuario autenticado debe ser owner del partner del pack.
        - El horario actual debe estar dentro de la ventana pickup_start/pickup_end.
        - La orden debe estar PENDIENTE o PAGADO y el pack tener stock “consumido” (ya manejado al crear).
        """
        order = self.get_object()
        pack = order.pack
        partner = pack.partner

        # Verificar que el partner pertenece a este usuario
        if partner.owner_id != request.user.id:
            return response.Response({"detail": "No sos el dueño de este comercio."}, status=status.HTTP_403_FORBIDDEN)

        now = timezone.now()
        if now < pack.pickup_start or now > pack.pickup_end:
            return response.Response({"detail": "Fuera de la franja de retiro."}, status=status.HTTP_400_BAD_REQUEST)

        if order.estado not in [Order.Estado.PENDIENTE, Order.Estado.PAGADO]:
            return response.Response({"detail": f"No se puede canjear una orden en estado {order.estado}."}, status=status.HTTP_400_BAD_REQUEST)

        order.estado = Order.Estado.RETIRADO
        order.save(update_fields=["estado"])
        return response.Response({"detail": "Orden marcada como RETIRADA ✅"}, status=status.HTTP_200_OK)