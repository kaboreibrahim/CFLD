import uuid

from django.db import models

from .choices import PAYMENT_MODE_CHOICES, upload_qr_code


class ComptePaiement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODE_CHOICES,
        verbose_name="Mode de paiement",
    )
    numero = models.CharField(max_length=100, verbose_name="Numéro / référence")
    nom_titulaire = models.CharField(max_length=160, verbose_name="Nom du titulaire")
    qr_code = models.ImageField(
        upload_to=upload_qr_code,
        blank=True,
        null=True,
        verbose_name="QR code",
    )
    lien = models.URLField(max_length=500, blank=True, default="", verbose_name="Lien de paiement")
    instructions = models.TextField(blank=True, default="", verbose_name="Instructions")
    est_actif = models.BooleanField(default=True, verbose_name="Compte actif")
    ordre_affichage = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ordre_affichage", "mode", "nom_titulaire"]
        verbose_name = "Compte de paiement"
        verbose_name_plural = "Comptes de paiement"

    def __str__(self):
        return f"{self.get_mode_display()} — {self.numero} ({self.nom_titulaire})"

    @property
    def label_court(self):
        return f"{self.get_mode_display()} · {self.nom_titulaire}"
