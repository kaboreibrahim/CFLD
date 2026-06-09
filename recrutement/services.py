"""
Services métier pour le recrutement CFLD.
Toute la logique de transformation candidature → joueur est ici,
indépendante des vues.
"""
from django.utils import timezone


def integrer_dans_effectif(candidature):
    """
    Crée le Joueur correspondant à une candidature acceptée.
    N'a aucun effet si le joueur existe déjà.
    """
    if hasattr(candidature, 'joueur') and candidature.joueur:
        return

    from effectif.models import Joueur

    Joueur.objects.create(
        nom=candidature.nom,
        prenom=candidature.prenom,
        date_naissance=candidature.date_naissance,
        sexe=candidature.sexe,
        categorie=candidature.categorie,
        nationalite=candidature.nationalite,
        adresse=candidature.adresse,
        numero=candidature.numero_prefere or 99,
        poste=candidature.poste,
        pied_fort=candidature.pied_fort,
        ancien_club=candidature.ancien_club,
        telephone_whatsapp=candidature.telephone_whatsapp,
        email=candidature.email,
        nom_parent=candidature.nom_parent,
        telephone_parent=candidature.telephone_parent,
        email_parent=candidature.email_parent,
        info_scolaire=candidature.info_scolaire,
        contact_urgence=candidature.contact_urgence,
        age=candidature.age,
        photo=candidature.photo,
        date_inscription=timezone.now().date(),
        actif=True,
        candidature=candidature,
    )
