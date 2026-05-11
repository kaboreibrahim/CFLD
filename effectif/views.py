from django.shortcuts import render
from .models import Joueur


def effectif(request):
    poste = request.GET.get('poste', 'all')
    joueurs = Joueur.objects.filter(actif=True)

    if poste in ('GK', 'DEF', 'MIL', 'ATT'):
        joueurs = joueurs.filter(poste=poste)

    counts = {
        'all': Joueur.objects.filter(actif=True).count(),
        'GK': Joueur.objects.filter(actif=True, poste='GK').count(),
        'DEF': Joueur.objects.filter(actif=True, poste='DEF').count(),
        'MIL': Joueur.objects.filter(actif=True, poste='MIL').count(),
        'ATT': Joueur.objects.filter(actif=True, poste='ATT').count(),
    }

    return render(request, 'effectif/effectif.html', {
        'joueurs': joueurs,
        'poste_actif': poste,
        'counts': counts,
    })
