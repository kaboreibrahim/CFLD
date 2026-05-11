from django.shortcuts import render
from medias.models import Article
from matchs.models import Match
from django.utils import timezone


def accueil(request):
    articles = Article.objects.filter(publie=True).order_by('-date_publication')[:3]
    prochain_match = Match.objects.filter(
        type_match='a_venir',
        date__gte=timezone.now()
    ).order_by('date').first()
    return render(request, 'pages/accueil.html', {
        'articles': articles,
        'prochain_match': prochain_match,
    })


def club(request):
    return render(request, 'pages/club.html')


def academie(request):
    return render(request, 'pages/academie.html')
