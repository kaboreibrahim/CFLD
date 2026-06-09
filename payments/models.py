import uuid
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from effectif.models import Joueur
from recrutement.models import Candidature


PAYMENT_MODE_CHOICES = [
    ("wave", "Wave"),
    ("orange_money", "Orange Money"),
    ("moov", "Moov"),
    ("mtn", "MTN"),
    ("virement", "Virement"),
    ("espece", "Espèce"),
]

VALIDATION_CHOICES = [
    ("pending", "En attente"),
    ("approved", "Validé"),
    ("rejected", "Refusé"),
]


def upload_qr_code(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/comptes/{instance.id}.{ext}"


def upload_capture_visite(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/visite_medicale/{instance.id}.{ext}"


def upload_capture_inscription(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/inscription/{instance.id}.{ext}"


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


class PaiementInscription(models.Model):
    # note: source of truth for the 1st versement auto-created on approval
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidature = models.ForeignKey(
        Candidature,
        on_delete=models.CASCADE,
        related_name="paiements_inscription",
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
        related_name="paiements_inscription",
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
        upload_to=upload_capture_inscription,
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
        related_name="inscriptions_enregistrees",
        verbose_name="Enregistré par",
    )
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inscriptions_validees",
        verbose_name="Validé par",
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Paiement inscription"
        verbose_name_plural = "Paiements inscription"
        indexes = [
            models.Index(fields=["statut_validation"], name="idx_inscription_statut"),
            models.Index(fields=["candidature"], name="idx_inscription_cand"),
        ]

    def __str__(self):
        return f"{self.candidature.nom_complet} — Inscription — {self.montant} FCFA"

    def clean(self):
        errors = {}
        if self.montant is not None and self.montant <= 0:
            errors["montant"] = "Le montant doit être strictement positif."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        ancien_statut = None
        if self.pk:
            try:
                ancien_statut = PaiementInscription.objects.values_list(
                    "statut_validation", flat=True
                ).get(pk=self.pk)
            except PaiementInscription.DoesNotExist:
                pass

        if self.statut_validation == "approved" and not self.date_validation:
            self.date_validation = timezone.now()
        elif self.statut_validation != "approved":
            self.date_validation = None
            self.valide_par = None

        super().save(*args, **kwargs)

        # Auto-création du premier versement quand on passe à "approved"
        if self.statut_validation == "approved" and ancien_statut != "approved":
            from .services import auto_creer_versement_inscription
            auto_creer_versement_inscription(self)

        # Suppression du versement auto si l'inscription est annulée
        elif ancien_statut == "approved" and self.statut_validation != "approved":
            from .services import supprimer_versement_inscription
            supprimer_versement_inscription(self)

    @property
    def est_valide(self):
        return self.statut_validation == "approved"

    @property
    def statut_label(self):
        return dict(VALIDATION_CHOICES).get(self.statut_validation, self.statut_validation)

    @property
    def versement_auto(self):
        """Retourne le VersementCotisation auto-créé depuis cette inscription."""
        from .models import VersementCotisation
        return VersementCotisation.objects.filter(source_inscription=self).first()


# ── COTISATION ANNUELLE ─────────────────────────────────────

COTISATION_STATUT_CHOICES = [
    ("en_cours", "En cours"),
    ("solde", "Soldé"),
    ("en_retard", "En retard"),
    ("suspendu", "Suspendu"),
]

VERSEMENT_TYPE_CHOICES = [
    ("premier", "1er versement"),
    ("mensuel", "Versement mensuel"),
    ("rattrapage", "Rattrapage"),
]

NB_VERSEMENTS_MENSUELS = 10
MONTANT_PREMIER_VERSEMENT = Decimal("200000")
MONTANT_MENSUEL = Decimal("100000")
MONTANT_TOTAL_DEFAUT = MONTANT_PREMIER_VERSEMENT + (MONTANT_MENSUEL * NB_VERSEMENTS_MENSUELS)


def upload_capture_versement(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/cotisations/{instance.id}.{ext}"


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
        max_digits=12, decimal_places=0,
        default=MONTANT_TOTAL_DEFAUT,
        verbose_name="Montant total (FCFA)",
    )
    statut = models.CharField(
        max_length=20, choices=COTISATION_STATUT_CHOICES,
        default="en_cours", db_index=True, verbose_name="Statut",
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
        "PaiementInscription",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="versement_cotisation",
        verbose_name="Paiement inscription source",
    )
    type_versement = models.CharField(
        max_length=20, choices=VERSEMENT_TYPE_CHOICES,
        default="mensuel", verbose_name="Type",
    )
    montant = models.DecimalField(
        max_digits=12, decimal_places=0, verbose_name="Montant (FCFA)",
    )
    compte_paiement = models.ForeignKey(
        ComptePaiement,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="versements_cotisation",
        verbose_name="Numéro utilisé pour le dépôt",
    )
    reference_transaction = models.CharField(
        max_length=120, blank=True, default="",
        verbose_name="Référence de transaction",
    )
    capture_depot = models.ImageField(
        upload_to=upload_capture_versement,
        blank=True, null=True,
        verbose_name="Capture d'écran du dépôt",
    )
    statut_validation = models.CharField(
        max_length=20, choices=VALIDATION_CHOICES,
        default="pending", db_index=True, verbose_name="Statut",
    )
    date_versement = models.DateField(default=timezone.localdate, verbose_name="Date du versement")
    notes = models.TextField(blank=True, default="", verbose_name="Notes")
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="versements_enregistres", verbose_name="Enregistré par",
    )
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="versements_valides", verbose_name="Validé par",
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_versement", "-date_creation"]
        verbose_name = "Versement cotisation"
        verbose_name_plural = "Versements cotisations"
        indexes = [
            models.Index(fields=["statut_validation"], name="idx_versement_statut"),
            models.Index(fields=["cotisation", "statut_validation"], name="idx_versement_cot_statut"),
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
