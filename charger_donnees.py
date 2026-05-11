"""
Script de chargement des données initiales CFLD.
Exécuter avec : python manage.py shell < charger_donnees.py
ou : python charger_donnees.py (si manage.py est configuré)
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from datetime import date, datetime
from django.utils import timezone
from effectif.models import Joueur
from matchs.models import Match, Classement
from medias.models import Article
from recrutement.models import Candidature

print("Chargement des données initiales...")

# Joueurs
joueurs_data = [
    ('Touré', 'Ibrahim', 1, 'GK', 24, 28, 0),
    ('Koffi', 'Yves', 12, 'GK', 19, 8, 0),
    ('Diop', 'Pape', 30, 'GK', 22, 5, 0),
    ('Coulibaly', 'Souleymane', 2, 'DEF', 27, 32, 1),
    ('Bamba', 'Adama', 3, 'DEF', 25, 29, 0),
    ('Yao', 'Émile', 4, 'DEF', 23, 25, 2),
    ('Sangaré', 'Karim', 5, 'DEF', 26, 31, 0),
    ('Diallo', 'Lassana', 14, 'DEF', 22, 18, 1),
    ('Konaté', 'Moussa', 22, 'DEF', 24, 22, 0),
    ('Brou', 'Étienne', 25, 'DEF', 21, 14, 0),
    ('Diaby', 'Cheick', 6, 'MIL', 26, 30, 3),
    ('Fofana', 'Drissa', 8, 'MIL', 24, 27, 4),
    ('Traoré', 'Ousmane', 10, 'MIL', 22, 24, 5),
    ('Gnagne', 'Yannick', 16, 'MIL', 25, 26, 2),
    ('Doumbia', 'Salif', 18, 'MIL', 23, 20, 3),
    ('Tagro', 'Aboubakar', 20, 'MIL', 21, 15, 1),
    ('Bah', 'Idriss', 28, 'MIL', 19, 10, 0),
    ('Soro', 'Mahamadou', 7, 'ATT', 23, 28, 8),
    ('Akré', 'Junior', 9, 'ATT', 25, 30, 12),
    ('Anoma', 'Kévin', 11, 'ATT', 22, 22, 7),
    ("N'Doye", 'Alassane', 17, 'ATT', 24, 25, 6),
    ('Kouadio', 'Brice', 19, 'ATT', 20, 14, 4),
]

if not Joueur.objects.exists():
    for nom, prenom, num, poste, age, matchs, buts in joueurs_data:
        Joueur.objects.create(
            nom=nom, prenom=prenom, numero=num, poste=poste,
            age=age, matchs_joues=matchs, buts=buts
        )
    print(f"  ✓ {len(joueurs_data)} joueurs créés")
else:
    print("  — Joueurs déjà présents")

# Matchs à venir
matchs_a_venir = [
    ('CFLD', 'Stella Club', True, None, None, datetime(2026, 5, 9, 16, 0), 'Stade Champroux, Abidjan', 'Ligue 1 CI', 18),
    ('Sporting Oran', 'CFLD', False, None, None, datetime(2026, 5, 16, 17, 30), 'Stade Aïn El Türck', 'CAF U17', None),
    ('CFLD', 'Africa Sports', True, None, None, datetime(2026, 5, 23, 16, 0), 'Stade Champroux, Abidjan', 'Ligue 1 CI', 19),
    ('EFYM', 'CFLD', False, None, None, datetime(2026, 5, 30, 15, 0), 'Yamoussoukro', 'Ligue 1 CI', 20),
    ('CFLD', 'Bouaké FC', True, None, None, datetime(2026, 6, 6, 16, 0), 'Stade Champroux, Abidjan', 'Ligue 1 CI', 21),
]

matchs_resultats = [
    ('CFLD', 'ASEC Mimosas', True, 3, 1, datetime(2026, 5, 2, 16, 0), 'Stade Champroux', 'Ligue 1 CI', 17),
    ('Sporting Gagnoa', 'CFLD', False, 1, 2, datetime(2026, 4, 25, 16, 0), 'Gagnoa', 'Ligue 1 CI', 16),
    ('CFLD', 'Bouaké FC', True, 0, 0, datetime(2026, 4, 18, 16, 0), 'Stade Champroux', 'Ligue 1 CI', 15),
    ('Daloa', 'CFLD', False, 2, 1, datetime(2026, 4, 11, 16, 0), 'Daloa', 'Ligue 1 CI', 14),
    ('CFLD', 'Africa Sports', True, 2, 0, datetime(2026, 4, 4, 16, 0), 'Stade Champroux', 'Ligue 1 CI', 13),
]

if not Match.objects.exists():
    for dom, ext, home, sd, se, dt, lieu, comp, j in matchs_a_venir:
        Match.objects.create(
            equipe_domicile=dom, equipe_exterieur=ext, est_domicile=home,
            date=timezone.make_aware(dt), lieu=lieu, competition=comp,
            journee=j, type_match='a_venir'
        )
    for dom, ext, home, sd, se, dt, lieu, comp, j in matchs_resultats:
        Match.objects.create(
            equipe_domicile=dom, equipe_exterieur=ext, est_domicile=home,
            score_domicile=sd, score_exterieur=se,
            date=timezone.make_aware(dt), lieu=lieu, competition=comp,
            journee=j, type_match='resultat'
        )
    print(f"  ✓ {len(matchs_a_venir)+len(matchs_resultats)} matchs créés")
else:
    print("  — Matchs déjà présents")

# Classement
classement_data = [
    ('ASEC Mimosas', 39, 17, 12, 3, 2, 38, 16, False),
    ('Africa Sports', 36, 17, 11, 3, 3, 32, 14, False),
    ('CFLD', 34, 17, 10, 4, 3, 28, 13, True),
    ('Stella Club', 31, 17, 9, 4, 4, 22, 14, False),
    ('Sporting Gagnoa', 29, 17, 8, 5, 4, 20, 14, False),
    ('Bouaké FC', 26, 17, 7, 5, 5, 18, 16, False),
    ('EFYM', 23, 17, 6, 5, 6, 15, 16, False),
    ('Daloa', 19, 17, 5, 4, 8, 14, 19, False),
]

if not Classement.objects.exists():
    for equipe, pts, j, v, n, d, bp, bc, cfld in classement_data:
        Classement.objects.create(
            equipe=equipe, points=pts, matchs_joues=j,
            victoires=v, nuls=n, defaites=d,
            buts_pour=bp, buts_contre=bc, est_cfld=cfld
        )
    print(f"  ✓ {len(classement_data)} équipes au classement")
else:
    print("  — Classement déjà présent")

# Articles
articles_data = [
    ('Les U17 s\'imposent 3—0 face à Africa Sports', 'Une démonstration collective au stade Champroux. Reportage et analyse tactique disponibles.', 'match', True),
    ('Stage à Yamoussoukro pour la promotion 2026', 'Trois jours de cohésion pour les U15 et U17 au centre sportif de Yamoussoukro.', 'academie', False),
    ('Nouveau partenariat avec Adidas Afrique', 'Le CFLD signe un accord d\'équipement exclusif avec Adidas pour les trois prochaines saisons.', 'club', False),
    ('Junior Akré signe professionnel en Belgique', 'Le buteur formé au CFLD rejoint le Standard de Liège pour un contrat de 3 ans.', 'joueur', False),
    ('Détection U13 — inscriptions ouvertes', 'La prochaine séance de détection pour les U13 se tiendra le samedi 17 mai au campus.', 'academie', False),
    ('Victoire 2—1 contre le Sporting Gagnoa', 'Soro et Akré signent la victoire en déplacement à Gagnoa. CFLD reste 3ᵉ au classement.', 'match', False),
]

if not Article.objects.exists():
    for titre, accroche, cat, une in articles_data:
        Article.objects.create(
            titre=titre, accroche=accroche, contenu=accroche,
            categorie=cat, en_une=une
        )
    print(f"  ✓ {len(articles_data)} articles créés")
else:
    print("  — Articles déjà présents")

# Candidatures de test
candidatures_data = [
    ('Kouassi', 'Yannick', date(2010, 3, 12), "Côte d'Ivoire", 'ATT', '+225 07 21 33 88 90', 'y.kouassi@email.com', 'pending'),
    ('Bamba', 'Aïcha', date(2011, 7, 4), "Côte d'Ivoire", 'MO', '+225 05 60 12 44 21', 'a.bamba@email.com', 'pending'),
    ('Coulibaly', 'Drissa', date(2009, 1, 20), 'Mali', 'DC', '+225 07 88 02 11 36', 'd.coulibaly@email.com', 'waiting'),
    ('Kéita', 'Maxime', date(2012, 9, 8), 'Burkina Faso', 'AIL', '+225 01 22 90 14 88', 'm.keita@email.com', 'pending'),
    ("N'Dri", 'Étienne', date(2008, 5, 15), "Côte d'Ivoire", 'GK', '+225 07 14 56 22 09', 'e.ndri@email.com', 'accepted'),
    ('Diop', 'Souleymane', date(2010, 11, 3), 'Sénégal', 'LAT', '+225 05 33 47 11 02', 's.diop@email.com', 'accepted'),
    ('Yao', 'Karim', date(2007, 8, 22), "Côte d'Ivoire", 'MD', '+225 07 90 18 65 41', 'k.yao@email.com', 'refused'),
    ('Bah', 'Junior', date(2011, 2, 17), 'Ghana', 'ATT', '+225 01 67 34 25 90', 'j.bah@email.com', 'pending'),
]

if not Candidature.objects.exists():
    for nom, prenom, dob, nat, poste, tel, email, statut in candidatures_data:
        Candidature.objects.create(
            nom=nom, prenom=prenom, date_naissance=dob,
            nationalite=nat, poste=poste,
            pied_fort='Droit', telephone_whatsapp=tel,
            email=email, statut=statut
        )
    print(f"  ✓ {len(candidatures_data)} candidatures de test créées")
else:
    print("  — Candidatures déjà présentes")

print("\n✓ Données initiales chargées avec succès !")
print("  Accès admin : /admin-cfld/login/  →  admin / cfld2026!")
print("  Django admin : /django-admin/  →  admin / cfld2026!")
