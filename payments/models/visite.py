import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from recrutement.models import Candidature

from .choices import VALIDATION_CHOICES, upload_capture_visite
from .compte import ComptePaiement


class PaiementVisiteMedicale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidature = models.ForeignKey(
        Candidature,
        on_delete=models.CASCADE,
        related_name="paiements_visite_medicale",
        verbose_name="Candidature",
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name="Montant (FCFA)",
    )
    compte_paiement = models.ForeignKey(
        ComptePaiement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paiements_visite",
        verbose_name="Numéro utilisé pour le dépôt",
    )
    reference_transaction = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Référence de transaction",
        help_text="Référence/ID visible sur la capture d'écran du dépôt",
    )
    capture_depot = models.ImageField(
        upload_to=upload_capture_visite,
        verbose_name="Capture d'écran du dépôt",
    )
    statut_validation = models.CharField(
        max_length=20,
        choices=VALIDATION_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="Statut",
    )
    date_paiement = models.DateField(default=timezone.localdate, verbose_name="Date du paiement")
    notes = models.TextField(blank=True, default="", verbose_name="Notes internes")
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visites_enregistrees",
        verbose_name="Enregistré par",
    )
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visites_validees",
        verbose_name="Validé par",
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Paiement visite médicale"
        verbose_name_plural = "Paiements visites médicales"
        indexes = [
            models.Index(fields=["statut_validation"], name="idx_visite_statut"),
            models.Index(fields=["candidature"], name="idx_visite_cand"),
        ]

    def __str__(self):
        return f"{self.candidature.nom_complet} — Visite médicale — {self.montant} FCFA"

    def clean(self):
        errors = {}
        if self.montant is not None and self.montant <= 0:
            errors["montant"] = "Le montant doit être strictement positif."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.statut_validation == "approved" and not self.date_validation:
            self.date_validation = timezone.now()
        elif self.statut_validation != "approved":
            self.date_validation = None
            self.valide_par = None
        super().save(*args, **kwargs)

    @property
    def est_valide(self):
        return self.statut_validation == "approved"

    @property
    def statut_label(self):
        return dict(VALIDATION_CHOICES).get(self.statut_validation, self.statut_validation)
