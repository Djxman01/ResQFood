from rest_framework import serializers
from .models import Partner, Pack, Order
from django.contrib.auth import get_user_model


class PartnerSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    class Meta:
        model = Partner
        fields = ["id", "nombre", "categoria", "imagen_url"]

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get("request")
        url = obj.imagen.url
        return request.build_absolute_uri(url) if request else url

class PackSerializer(serializers.ModelSerializer):
    partner_nombre = serializers.CharField(source="partner.nombre", read_only=True)
    partner_imagen_url = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Pack
        fields = ["id","partner","partner_nombre","titulo","etiqueta","precio_original","imagen_url","partner_imagen_url",
                  "precio_oferta","stock","pickup_start","pickup_end","creado_at"]
        
    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get("request")
        url = obj.imagen.url
        return request.build_absolute_uri(url) if request else url

    def get_partner_imagen_url(self, obj):
        if not getattr(obj.partner, "imagen", None):
            return None
        request = self.context.get("request")
        url = obj.partner.imagen.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        # Merge instance values on partial updates to compare effective values
        instance = getattr(self, "instance", None)

        def get_val(key):
            if key in attrs:
                return attrs.get(key)
            if instance is not None:
                return getattr(instance, key, None)
            return None

        pickup_start = get_val("pickup_start")
        pickup_end = get_val("pickup_end")
        precio_original = get_val("precio_original")
        precio_oferta = get_val("precio_oferta")

        errors = {}

        # Time window rule: end must be strictly greater than start
        if pickup_start is not None and pickup_end is not None:
            if not (pickup_end > pickup_start):
                errors["pickup_end"] = "pickup_end must be greater than pickup_start"

        # Price rule: oferta <= original
        if precio_original is not None and precio_oferta is not None:
            try:
                if precio_oferta > precio_original:
                    errors["precio_oferta"] = "precio_oferta must be <= precio_original"
            except TypeError:
                # Let DRF field-level validators handle type/format errors
                pass

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    pack_titulo = serializers.CharField(source="pack.titulo", read_only=True)

    class Meta:
        model = Order
        fields = ["id","user","pack","pack_titulo","precio_pagado","estado","creado_at",]
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
    

class OrderLiteSerializer(serializers.ModelSerializer):
    pack_titulo = serializers.CharField(source="pack.titulo", read_only=True)
    partner_nombre = serializers.CharField(source="pack.partner.nombre", read_only=True)
    imagen = serializers.ImageField(source="pack.imagen", read_only=True)
    pickup_start = serializers.DateTimeField(source="pack.pickup_start", read_only=True)
    pickup_end = serializers.DateTimeField(source="pack.pickup_end", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "estado", "precio_pagado", "creado_at",
            "pack", "pack_titulo", "partner_nombre", "imagen",
            "pickup_start", "pickup_end"
        ]


User = get_user_model()

