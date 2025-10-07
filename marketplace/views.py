from rest_framework import viewsets, permissions, decorators, response, status, filters
from .models import Partner, Pack, Order
from .serializers import PartnerSerializer, PackSerializer, OrderSerializer
from .permissions import IsPartner
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView



class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [permissions.IsAuthenticated]

class PackViewSet(viewsets.ModelViewSet):
    queryset = Pack.objects.select_related("partner").all()
    serializer_class = PackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["titulo", "etiqueta", "partner__nombre"]
    ordering_fields = ["precio_oferta", "creado_at"]
    filterset_fields = ["etiqueta", "partner"]

    def get_queryset(self):
        qs = Pack.objects.select_related("partner").order_by("-creado_at")
        v = (self.request.query_params.get("vigentes") or "").lower()
        if v in ("1", "true", "yes"):
            now = timezone.now()
            qs = qs.filter(stock__gt=0, pickup_start__lte=now, pickup_end__gte=now)
        return qs

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reservar(self, request, pk=None):
        user = request.user
        now = timezone.now()

        with transaction.atomic():
            # Lock de fila para evitar reservas simultáneas
            pack = Pack.objects.select_for_update().get(pk=pk)

            # Ventana de retiro y disponibilidad
            if pack.stock <= 0:
                return Response({"detail": "Sin stock disponible."}, status=status.HTTP_409_CONFLICT)
           # Permitimos reservar antes; solo bloqueamos si ya pasó la ventana
            if now > pack.pickup_end:
                return Response({"detail": "La franja de retiro ya expiró."}, status=status.HTTP_409_CONFLICT)


            # Evitar duplicadas
            if Order.objects.filter(user=user, pack=pack, estado__in=[Order.Estado.PENDIENTE, Order.Estado.PAGADO]).exists():
                return Response({"detail": "Ya reservaste este pack."}, status=status.HTTP_409_CONFLICT)

            # Crear la orden (Order.save() validará y descontará stock atómicamente)
            try:
                order = Order.objects.create(
                    user=user,
                    pack=pack,
                    precio_pagado=pack.precio_oferta,
                    estado=Order.Estado.PENDIENTE,
                )
            except ValidationError as e:
                # Si fallan las validaciones de clean() (p.ej. stock/ventana), devolver 409/400
                return Response({"detail": e.message}, status=status.HTTP_409_CONFLICT)

            # Refrescar pack para conocer el stock actualizado
            pack.refresh_from_db(fields=["stock"])

            return Response(
                {"detail": "Pack reservado ✅", "order_id": order.id, "nuevo_stock": pack.stock},
                status=status.HTTP_201_CREATED,
            )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user", "pack", "pack__partner").all().order_by("-creado_at")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada usuario ve sus propias órdenes
        return super().get_queryset().filter(user=self.request.user)
    
    def get_serializer_class(self):
        # Para list y retrieve devolvemos el enriquecido
        if self.action in ["list", "retrieve"]:
            from .serializers import OrderLiteSerializer
            return OrderLiteSerializer
        return super().get_serializer_class()

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
    
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.user_id != request.user.id:
            return response.Response({"detail": "No podés cancelar una orden de otro usuario."}, status=status.HTTP_403_FORBIDDEN)

        if order.estado not in [Order.Estado.PENDIENTE, Order.Estado.PAGADO]:
            return response.Response({"detail": f"No se puede cancelar una orden en estado {order.estado}."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if now > order.pack.pickup_end:
            return response.Response({"detail": "La franja ya expiró, no se puede cancelar."}, status=status.HTTP_409_CONFLICT)

        with transaction.atomic():
            # Cambiar estado
            order.estado = Order.Estado.CANCELADO
            order.save(update_fields=["estado"])
            # Devolver stock
            type(order.pack).objects.filter(pk=order.pack_id).update(stock=F("stock") + 1)

        return response.Response({"detail": "Orden cancelada y stock devuelto ✅"}, status=status.HTTP_200_OK)
    

class MisReservasView(LoginRequiredMixin, ListView):
    template_name = "marketplace/mis_reservas.html"
    context_object_name = "orders"
    paginate_by = 12  # opcional

    def get_queryset(self):
        # Lo mismo que la API: solo mis órdenes, con joins del pack/partner
        return (
            Order.objects
            .select_related("pack", "pack__partner")
            .filter(user=self.request.user)
            .order_by("-creado_at")
        )