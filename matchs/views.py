from django.shortcuts import render
from .models import Match, Classement


def matchs(request):
    a_venir = Match.objects.filter(type_match='a_venir').order_by('date')
    resultats = Match.objects.filter(type_match='resultat').order_by('-date')
    classement = Classement.objects.filter(saison='2025-2026')

    return render(request, 'matchs/matchs.html', {
        'a_venir': a_venir,
        'resultats': resultats,
        'classement': classement,
        'nb_a_venir': a_venir.count(),
        'nb_resultats': resultats.count(),
        'nb_equipes': classement.count(),
    })
