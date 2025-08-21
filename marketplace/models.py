from django.db import models


# marketplace/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Partner(models.Model):
    class Rubro(models.TextChoices):
        SUPER = "super", "Supermercado"
        KIOSCO = "kiosco", "Kiosco"
        VERDULERIA = "verduleria", "Verdulería"
        RESTO = "resto", "Restaurante"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="partners")
    nombre = models.CharField(max_length=120)
    rubro = models.CharField(max_length=20, choices=Rubro.choices)
    direccion = models.CharField(max_length=200)
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Pack(models.Model):
    class Etiqueta(models.TextChoices):
        POR_VENCER = "por_vencer", "Por vencer"
        EXCEDENTE = "excedente", "Excedente"

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="packs")
    titulo = models.CharField(max_length=140)
    etiqueta = models.CharField(max_length=20, choices=Etiqueta.choices)
    precio_original = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=1)
    pickup_start = models.DateTimeField()
    pickup_end = models.DateTimeField()
    creado_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.partner.nombre}"

class Order(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PAGADO    = "pagado",    "Pagado"     # si más adelante integrás pagos
        RETIRADO  = "retirado",  "Retirado"
        CANCELADO = "cancelado", "Cancelado"
        EXPIRADO  = "expirado",  "Expirado"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    pack = models.ForeignKey(Pack, on_delete=models.PROTECT, related_name="orders")
    precio_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    creado_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validaciones básicas
        if self.pack.stock <= 0:
            raise ValidationError("No hay stock disponible para este pack.")
        if timezone.now() > self.pack.pickup_end:
            raise ValidationError("La franja de retiro de este pack ya expiró.")

    def save(self, *args, **kwargs):
        creating = self._state.adding
        self.full_clean()  # ejecuta clean() antes de guardar
        super().save(*args, **kwargs)
        # Si la orden es nueva, reducir stock del pack
        if creating:
            Pack.objects.filter(pk=self.pack_id).update(stock=models.F("stock") - 1)
