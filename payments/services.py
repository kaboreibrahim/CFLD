"""
Services métier pour les cotisations et versements CFLD.
Toute la logique de calcul est ici, indépendante des vues.
"""
from decimal import Decimal
from django.utils import timezone

MONTANT_ECHEANCE = Decimal("100000")
NB_ECHEANCES = 10
MONTANT_TOTAL = MONTANT_ECHEANCE * NB_ECHEANCES  # 1 000 000 FCFA


# ── CALCUL DES ÉCHÉANCES ────────────────────────────────────

def calculer_echeances(cotisation):
    """
    Calcule les 10 échéances à partir du total des versements validés.

    Règles :
    - Chaque échéance = 100 000 FCFA.
    - Un versement supérieur à 100 000 FCFA solde l'échéance en cours
      et reporte l'excédent sur la suivante.
    - Un versement inférieur = acompte ; l'échéance n'est soldée que
      quand le cumul atteint 100 000 FCFA.
    - Les calculs se basent UNIQUEMENT sur les versements validés (approved).
    """
    total_verse = cotisation.total_verse  # sum of approved versements (Decimal)
    montant_restant = total_verse

    echeances = []
    for num in range(1, NB_ECHEANCES + 1):
        if montant_restant >= MONTANT_ECHEANCE:
            statut = "solde"
            montant_paye = MONTANT_ECHEANCE
            montant_restant_ech = Decimal("0")
        elif montant_restant > 0:
            statut = "partiel"
            montant_paye = montant_restant
            montant_restant_ech = MONTANT_ECHEANCE - montant_restant
        else:
            statut = "non_paye"
            montant_paye = Decimal("0")
            montant_restant_ech = MONTANT_ECHEANCE

        echeances.append({
            "num": num,
            "label": "1er versement" if num == 1 else f"Versement {num}",
            "montant_attendu": MONTANT_ECHEANCE,
            "montant_paye": montant_paye,
            "montant_restant": montant_restant_ech,
            "statut": statut,
        })
        montant_restant = max(montant_restant - MONTANT_ECHEANCE, Decimal("0"))

    nb_soldes = sum(1 for e in echeances if e["statut"] == "solde")
    nb_partiels = sum(1 for e in echeances if e["statut"] == "partiel")
    nb_non_payes = sum(1 for e in echeances if e["statut"] == "non_paye")
    total_restant = max(MONTANT_TOTAL - total_verse, Decimal("0"))

    return {
        "echeances": echeances,
        "nb_soldes": nb_soldes,
        "nb_partiels": nb_partiels,
        "nb_non_payes": nb_non_payes,
        "nb_echeances": NB_ECHEANCES,
        "montant_total": MONTANT_TOTAL,
        "total_verse": total_verse,
        "total_restant": total_restant,
        "progression_pct": min(int((total_verse / MONTANT_TOTAL) * 100), 100) if MONTANT_TOTAL > 0 else 0,
    }


def prochaine_echeance(cotisation):
    """Retourne la première échéance non soldée."""
    data = calculer_echeances(cotisation)
    for e in data["echeances"]:
        if e["statut"] != "solde":
            return e
    return None


# ── AUTO-CRÉATION VERSEMENT DEPUIS INSCRIPTION ─────────────

def auto_creer_versement_inscription(paiement_inscription):
    """
    Crée automatiquement un VersementCotisation (type='premier') depuis un
    PaiementInscription qui vient d'être approuvé.
    Retourne le versement créé, ou None si impossible / déjà créé.
    """
    from .models import CotisationAnnuelle, VersementCotisation

    # Vérifier que la candidature a un joueur accepté
    candidature = paiement_inscription.candidature
    joueur = getattr(candidature, 'joueur', None)
    if not joueur:
        return None

    # Éviter la double-création
    if VersementCotisation.objects.filter(
        source_inscription=paiement_inscription
    ).exists():
        return None

    annee = paiement_inscription.date_paiement.year
    cotisation, _ = CotisationAnnuelle.objects.get_or_create(
        joueur=joueur,
        annee=annee,
    )

    versement = VersementCotisation(
        cotisation=cotisation,
        source_inscription=paiement_inscription,
        type_versement="premier",
        montant=paiement_inscription.montant,
        compte_paiement=paiement_inscription.compte_paiement,
        reference_transaction=paiement_inscription.reference_transaction,
        statut_validation="approved",
        date_versement=paiement_inscription.date_paiement,
        notes="Généré automatiquement depuis le paiement d'inscription validé.",
        valide_par=paiement_inscription.valide_par,
        date_validation=paiement_inscription.date_validation or timezone.now(),
    )
    # Copier la capture si présente
    if paiement_inscription.capture_depot:
        versement.capture_depot = paiement_inscription.capture_depot
    versement.save()
    return versement


def supprimer_versement_inscription(paiement_inscription):
    """
    Supprime le VersementCotisation auto-créé si l'inscription est annulée
    ou rejetée après avoir été approuvée.
    """
    from .models import VersementCotisation
    VersementCotisation.objects.filter(
        source_inscription=paiement_inscription
    ).delete()


# ── NUMÉROTATION DES REÇUS ─────────────────────────────────

def generer_numero_recu(objet):
    """Génère un numéro de reçu lisible depuis un UUID."""
    uid = str(objet.id).replace("-", "").upper()[:8]
    date = getattr(objet, 'date_paiement', None) or getattr(objet, 'date_versement', None)
    if date:
        return f"REC-{date.strftime('%Y%m%d')}-{uid}"
    return f"REC-{uid}"
