import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from effectif.models import Joueur

from .choices import (
    COTISATION_STATUT_CHOICES,
    MONTANT_MENSUEL,
    MONTANT_PREMIER_VERSEMENT,
    MONTANT_TOTAL_DEFAUT,
    NB_VERSEMENTS_MENSUELS,
    VALIDATION_CHOICES,
    VERSEMENT_TYPE_CHOICES,
    upload_capture_versement,
)
from .compte import ComptePaiement


class CotisationAnnuelle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    joueur = models.ForeignKey(
        Joueur,
        on_delete=models.CASCADE,
        related_name="cotisations_annuelles",
        verbose_name="Joueur",
    )
    annee = models.PositiveIntegerField(db_index=True, verbose_name="Année")
    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=MONTANT_TOTAL_DEFAUT,
        verbose_name="Montant total (FCFA)",
    )
    statut = models.CharField(
        max_length=20,
        choices=COTISATION_STATUT_CHOICES,
        default="en_cours",
        db_index=True,
        verbose_name="Statut",
    )
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-annee", "joueur__nom", "joueur__prenom"]
        verbose_name = "Cotisation annuelle"
        verbose_name_plural = "Cotisations annuelles"
        constraints = [
            models.UniqueConstraint(
                fields=["joueur", "annee"],
                name="uq_cotisation_joueur_annee",
            )
        ]
        indexes = [
            models.Index(fields=["annee"], name="idx_cotisation_annee"),
            models.Index(fields=["statut"], name="idx_cotisation_statut"),
        ]

    def __str__(self):
        return f"{self.joueur.nom_complet} — {self.annee}"

    @property
    def total_verse(self):
        result = self.versements.filter(statut_validation="approved").aggregate(
            total=models.Sum("montant")
        )["total"]
        return result or Decimal("0")

    @property
    def reste_a_payer(self):
        return max(self.montant_total - self.total_verse, Decimal("0"))

    @property
    def progression_pct(self):
        if self.montant_total <= 0:
            return 100
        return min(int((self.total_verse / self.montant_total) * 100), 100)

    @property
    def nb_versements_valides(self):
        return self.versements.filter(statut_validation="approved").count()

    @property
    def nb_versements_en_attente(self):
        return self.versements.filter(statut_validation="pending").count()

    @property
    def est_solde(self):
        return self.total_verse >= self.montant_total

    @property
    def dernier_versement(self):
        return self.versements.filter(
            statut_validation="approved"
        ).order_by("-date_versement").first()

    def recalculer_statut(self):
        if self.statut == "suspendu":
            return
        new = "solde" if self.est_solde else "en_cours"
        if self.statut != new:
            self.statut = new
            self.save(update_fields=["statut"])


class VersementCotisation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cotisation = models.ForeignKey(
        CotisationAnnuelle,
        on_delete=models.CASCADE,
        related_name="versements",
        verbose_name="Cotisation",
    )
    source_inscription = models.OneToOneField(
        "payments.PaiementInscription",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versement_cotisation",
        verbose_name="Paiement inscription source",
    )
    type_versement = models.CharField(
        max_length=20,
        choices=VERSEMENT_TYPE_CHOICES,
        default="mensuel",
        verbose_name="Type",
    )
    montant = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Montant (FCFA)",
    )
    compte_paiement = models.ForeignKey(
        ComptePaiement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versements_cotisation",
        verbose_name="Numéro utilisé pour le dépôt",
    )
    reference_transaction = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Référence de transaction",
    )
    capture_depot = models.ImageField(
        upload_to=upload_capture_versement,
        blank=True,
        null=True,
        verbose_name="Capture d'écran du dépôt",
    )
    statut_validation = models.CharField(
        max_length=20,
        choices=VALIDATION_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="Statut",
    )
    date_versement = models.DateField(default=timezone.localdate, verbose_name="Date du versement")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versements_enregistres",
        verbose_name="Enregistré par",
    )
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="versements_valides",
        verbose_name="Validé par",
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_versement", "-date_creation"]
        verbose_name = "Versement cotisation"
        verbose_name_plural = "Versements cotisations"
        indexes = [
            models.Index(fields=["statut_validation"], name="idx_versement_statut"),
            models.Index(
                fields=["cotisation", "statut_validation"],
                name="idx_versement_cot_statut",
            ),
        ]

    def __str__(self):
        return (
            f"{self.cotisation.joueur.nom_complet} — "
            f"{self.get_type_versement_display()} — {self.montant} FCFA"
        )

    def save(self, *args, **kwargs):
        if self.statut_validation == "approved" and not self.date_validation:
            self.date_validation = timezone.now()
        elif self.statut_validation != "approved":
            self.date_validation = None
            self.valide_par = None
        super().save(*args, **kwargs)
        self.cotisation.recalculer_statut()

    @property
    def est_valide(self):
        return self.statut_validation == "approved"
