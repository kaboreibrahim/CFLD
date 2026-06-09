from decimal import Decimal

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


def upload_qr_code(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/comptes/{instance.id}.{ext}"


def upload_capture_visite(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/visite_medicale/{instance.id}.{ext}"


def upload_capture_inscription(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/inscription/{instance.id}.{ext}"


def upload_capture_versement(instance, filename):
    ext = filename.split(".")[-1]
    return f"paiements/cotisations/{instance.id}.{ext}"
