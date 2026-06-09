from django.shortcuts import render
from django.utils import timezone

from contact.models import Message
from effectif.models import Joueur
from matchs.models import Match
from medias.models import Article
from recrutement.models import Candidature

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_dashboard(request):
    ctx = base_ctx(request, 'dashboard')
    ctx.update({
        'joueurs_count':    Joueur.objects.filter(actif=True).count(),
        'matchs_count':     Match.objects.filter(type_match='a_venir', date__gte=timezone.now()).count(),
        'articles_count':   Article.objects.filter(publie=True).count(),
        'total_cand':       Candidature.objects.count(),
        'total_msg':        Message.objects.count(),
        'recent_cands':     Candidature.objects.order_by('-date_soumission')[:6],
        'prochains_matchs': Match.objects.filter(type_match='a_venir', date__gte=timezone.now()).order_by('date')[:4],
        'recent_msgs':      Message.objects.order_by('-date_envoi')[:5],
    })
    return render(request, 'admin_cfld/dashboard.html', ctx)
