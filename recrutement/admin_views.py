from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from effectif.models import Joueur
from matchs.models import Match, Classement
from medias.models import Article, Photo, Video
from recrutement.models import Candidature
from contact.models import Message
from pages.models import InfoTicker

from effectif.forms import JoueurForm
from matchs.forms import MatchForm, ClassementForm
from medias.forms import ArticleForm, PhotoForm, VideoForm
from pages.forms import InfoTickerForm


# ── Décorateur staff ─────────────────────────────────────────
def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def _base_ctx(request, section=''):
    """Contexte commun injecté dans tous les templates admin."""
    return {
        'pending_count': Candidature.objects.filter(statut='pending').count(),
        'unread_count':  Message.objects.filter(lu=False).count(),
        'section':       section,
    }


# ── TABLEAU DE BORD ──────────────────────────────────────────
@staff_required
def admin_dashboard(request):
    ctx = _base_ctx(request, 'dashboard')
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


# ── JOUEURS ──────────────────────────────────────────────────
@staff_required
def admin_joueurs(request):
    q     = request.GET.get('q', '')
    poste = request.GET.get('poste', 'all')
    qs    = Joueur.objects.all()
    if q:
        qs = qs.filter(nom__icontains=q) | qs.filter(prenom__icontains=q)
    if poste != 'all':
        qs = qs.filter(poste=poste)
    ctx = _base_ctx(request, 'joueurs')
    ctx.update({'joueurs': qs, 'q': q, 'poste_actif': poste,
                'total': Joueur.objects.count()})
    return render(request, 'admin_cfld/joueurs.html', ctx)


@staff_required
def admin_joueur_form(request, pk=None):
    obj  = get_object_or_404(Joueur, pk=pk) if pk else None
    form = JoueurForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_joueurs')
    ctx = _base_ctx(request, 'joueurs')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/joueur_form.html', ctx)


@staff_required
def admin_joueur_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Joueur, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── MATCHS ───────────────────────────────────────────────────
@staff_required
def admin_matchs(request):
    type_m = request.GET.get('type', 'all')
    qs = Match.objects.all()
    if type_m != 'all':
        qs = qs.filter(type_match=type_m)
    ctx = _base_ctx(request, 'matchs')
    ctx.update({'matchs': qs, 'type_actif': type_m,
                'total': Match.objects.count()})
    return render(request, 'admin_cfld/matchs.html', ctx)


@staff_required
def admin_match_form(request, pk=None):
    obj  = get_object_or_404(Match, pk=pk) if pk else None
    form = MatchForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_matchs')
    ctx = _base_ctx(request, 'matchs')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/match_form.html', ctx)


@staff_required
def admin_match_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Match, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── CLASSEMENT ───────────────────────────────────────────────
@staff_required
def admin_classement(request):
    saison = request.GET.get('saison', '')
    qs = Classement.objects.all()
    if saison:
        qs = qs.filter(saison=saison)
    saisons = Classement.objects.values_list('saison', flat=True).distinct()
    ctx = _base_ctx(request, 'classement')
    ctx.update({'classement': qs, 'saison': saison, 'saisons': saisons})
    return render(request, 'admin_cfld/classement.html', ctx)


@staff_required
def admin_classement_form(request, pk=None):
    obj  = get_object_or_404(Classement, pk=pk) if pk else None
    form = ClassementForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_classement')
    ctx = _base_ctx(request, 'classement')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/classement_form.html', ctx)


@staff_required
def admin_classement_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Classement, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── ARTICLES ─────────────────────────────────────────────────
@staff_required
def admin_articles(request):
    q   = request.GET.get('q', '')
    cat = request.GET.get('cat', 'all')
    qs  = Article.objects.all()
    if q:
        qs = qs.filter(titre__icontains=q)
    if cat != 'all':
        qs = qs.filter(categorie=cat)
    ctx = _base_ctx(request, 'articles')
    ctx.update({'articles': qs, 'q': q, 'cat_actif': cat,
                'total': Article.objects.count()})
    return render(request, 'admin_cfld/articles.html', ctx)


@staff_required
def admin_article_form(request, pk=None):
    obj  = get_object_or_404(Article, pk=pk) if pk else None
    form = ArticleForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_articles')
    ctx = _base_ctx(request, 'articles')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/article_form.html', ctx)


@staff_required
def admin_article_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Article, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── PHOTOS ───────────────────────────────────────────────────
@staff_required
def admin_photos(request):
    qs = Photo.objects.all()
    ctx = _base_ctx(request, 'photos')
    ctx.update({'photos': qs})
    return render(request, 'admin_cfld/photos.html', ctx)


@staff_required
def admin_photo_form(request, pk=None):
    obj  = get_object_or_404(Photo, pk=pk) if pk else None
    form = PhotoForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_photos')
    ctx = _base_ctx(request, 'photos')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/photo_form.html', ctx)


@staff_required
def admin_photo_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Photo, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── VIDÉOS ───────────────────────────────────────────────────
@staff_required
def admin_videos(request):
    qs = Video.objects.all()
    ctx = _base_ctx(request, 'videos')
    ctx.update({'videos': qs})
    return render(request, 'admin_cfld/videos.html', ctx)


@staff_required
def admin_video_form(request, pk=None):
    obj  = get_object_or_404(Video, pk=pk) if pk else None
    form = VideoForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_videos')
    ctx = _base_ctx(request, 'videos')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/video_form.html', ctx)


@staff_required
def admin_video_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Video, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── CANDIDATURES ─────────────────────────────────────────────
@staff_required
def admin_candidatures(request):
    statut = request.GET.get('statut', 'all')
    q      = request.GET.get('q', '')
    qs     = Candidature.objects.all()
    if statut in ('pending', 'waiting', 'accepted', 'refused'):
        qs = qs.filter(statut=statut)
    if q:
        qs = (qs.filter(nom__icontains=q) | qs.filter(prenom__icontains=q)
              | qs.filter(email__icontains=q) | qs.filter(reference__icontains=q))
    stats = {
        'total':    Candidature.objects.count(),
        'pending':  Candidature.objects.filter(statut='pending').count(),
        'accepted': Candidature.objects.filter(statut='accepted').count(),
        'refused':  Candidature.objects.filter(statut='refused').count(),
        'waiting':  Candidature.objects.filter(statut='waiting').count(),
    }
    ctx = _base_ctx(request, 'candidatures')
    ctx.update({'candidatures': qs, 'stats': stats,
                'statut_actif': statut, 'recherche': q})
    return render(request, 'admin_cfld/candidatures.html', ctx)


@staff_required
def action_candidature(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    c = get_object_or_404(Candidature, pk=pk)
    action = request.POST.get('action')
    MAP = {'accept': 'accepted', 'refuse': 'refused', 'wait': 'waiting'}
    if action in MAP:
        c.statut = MAP[action]
        c.save()
    elif action == 'notify':
        c.notifie = True
        c.save()
    else:
        return JsonResponse({'error': 'Action inconnue'}, status=400)
    LABELS = {'pending': 'En attente', 'waiting': 'Mise en attente',
              'accepted': 'Acceptée', 'refused': 'Refusée'}
    return JsonResponse({'success': True, 'statut': c.statut,
                         'label': LABELS.get(c.statut, c.statut)})


# ── MESSAGES ─────────────────────────────────────────────────
@staff_required
def admin_messages(request):
    filtre = request.GET.get('filtre', 'all')
    qs = Message.objects.all()
    if filtre == 'non_lu':
        qs = qs.filter(lu=False)
    ctx = _base_ctx(request, 'messages')
    ctx.update({'messages_list': qs, 'filtre': filtre,
                'total': Message.objects.count()})
    return render(request, 'admin_cfld/messages.html', ctx)


@staff_required
def admin_message_detail(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if not msg.lu:
        msg.lu = True
        msg.save()
    ctx = _base_ctx(request, 'messages')
    ctx.update({'msg': msg})
    return render(request, 'admin_cfld/message_detail.html', ctx)


@staff_required
def admin_message_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(Message, pk=pk).delete()
    return JsonResponse({'ok': True})


# ── TICKER ───────────────────────────────────────────────────
@staff_required
def admin_ticker(request):
    qs = InfoTicker.objects.all()
    ctx = _base_ctx(request, 'ticker')
    ctx.update({'items': qs})
    return render(request, 'admin_cfld/ticker.html', ctx)


@staff_required
def admin_ticker_form(request, pk=None):
    obj  = get_object_or_404(InfoTicker, pk=pk) if pk else None
    form = InfoTickerForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_ticker')
    ctx = _base_ctx(request, 'ticker')
    ctx.update({'form': form, 'obj': obj})
    return render(request, 'admin_cfld/ticker_form.html', ctx)


@staff_required
def admin_ticker_delete(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    get_object_or_404(InfoTicker, pk=pk).delete()
    return JsonResponse({'ok': True})
