from rest_framework import serializers
from .models import Partner, Pack, Order

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = "__all__"

class PackSerializer(serializers.ModelSerializer):
    partner_nombre = serializers.CharField(source="partner.nombre", read_only=True)
    class Meta:
        model = Pack
        fields = ["id","partner","partner_nombre","titulo","etiqueta","precio_original",
                  "precio_oferta","stock","pickup_start","pickup_end","creado_at"]

class OrderSerializer(serializers.ModelSerializer):
    pack_titulo = serializers.CharField(source="pack.titulo", read_only=True)

    class Meta:
        model = Order
        fields = ["id","user","pack","pack_titulo","precio_pagado","estado","creado_at"]
        read_only_fields = ["user","estado","creado_at"]

    def validate(self, attrs):
        pack = attrs.get("pack")
        if pack and pack.stock <= 0:
            raise serializers.ValidationError("No hay stock para este pack.")
        return attrs

    def create(self, validated_data):
        # setea el usuario que crea la orden
        validated_data["user"] = self.context["request"].user
        # precio pagado = precio oferta (por ahora)
        validated_data.setdefault("precio_pagado", validated_data["pack"].precio_oferta)
        order = super().create(validated_data)
        return order
