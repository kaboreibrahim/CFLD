from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import SEOPage

PAGE_IDS_DEFAUT = [
    ('accueil', 'Page d\'accueil'),
    ('club', 'Page Club'),
    ('academie', 'Page Académie / Centre de formation'),
    ('effectif', 'Page Effectif'),
    ('matchs', 'Page Matchs'),
    ('medias', 'Page Actualités'),
    ('inscription', 'Page Inscription'),
    ('contact', 'Page Contact'),
    ('equipe_u10_masculin', 'Équipe U10 Masculin'),
    ('equipe_u13_masculin', 'Équipe U13 Masculin'),
    ('equipe_u15_masculin', 'Équipe U15 Masculin'),
    ('equipe_u17_masculin', 'Équipe U17+ Masculin'),
    ('equipe_u12_feminin', 'Équipe U12 Féminin'),
    ('equipe_u15_feminin', 'Équipe U15 Féminin'),
]
