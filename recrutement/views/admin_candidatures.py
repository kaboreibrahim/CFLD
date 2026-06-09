import os

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render

from recrutement.email_utils import envoyer_refus_inscription, envoyer_validation_inscription
from recrutement.models import Candidature
from recrutement.pdf_utils import generer_pdf_inscription
from recrutement.services import integrer_dans_effectif

from .admin_utils import base_ctx, staff_required


@staff_required
def admin_candidatures(request):
    statut = request.GET.get('statut', 'all')
    q = request.GET.get('q', '')
    qs = Candidature.objects.exclude(statut='accepted')
    if statut in ('pending', 'waiting', 'refused'):
        qs = qs.filter(statut=statut)
    if q:
        qs = (qs.filter(nom__icontains=q) | qs.filter(prenom__icontains=q)
              | qs.filter(email__icontains=q) | qs.filter(reference__icontains=q))
    stats = {
        'total':   Candidature.objects.exclude(statut='accepted').count(),
        'pending': Candidature.objects.filter(statut='pending').count(),
        'waiting': Candidature.objects.filter(statut='waiting').count(),
        'refused': Candidature.objects.filter(statut='refused').count(),
    }
    non_migrees = Candidature.objects.filter(statut='accepted').filter(joueur__isnull=True)
    ctx = base_ctx(request, 'candidatures')
    ctx.update({'candidatures': qs, 'stats': stats,
                'statut_actif': statut, 'recherche': q,
                'non_migrees_count': non_migrees.count()})
    return render(request, 'admin_cfld/candidatures.html', ctx)


@staff_required
def admin_migrer_acceptees(request):
    """Migre en masse les candidatures acceptées sans joueur lié."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    non_migrees = Candidature.objects.filter(statut='accepted').filter(joueur__isnull=True)
    count = 0
    errors = []
    for c in non_migrees:
        try:
            integrer_dans_effectif(c)
            count += 1
        except Exception as e:
            errors.append(f"{c.reference}: {e}")
    return JsonResponse({'ok': True, 'migres': count, 'errors': errors})


@staff_required
def action_candidature(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    c = get_object_or_404(Candidature, pk=pk)
    action = request.POST.get('action')
    MAP = {'accept': 'accepted', 'refuse': 'refused', 'wait': 'waiting'}
    if action in MAP:
        ancien_statut = c.statut
        c.statut = MAP[action]
        c.save()
        if action == 'accept':
            try:
                generer_pdf_inscription(c)
            except Exception:
                pass
            integrer_dans_effectif(c)
            try:
                envoyer_validation_inscription(c)
            except Exception:
                pass
        elif action == 'refuse' and ancien_statut != 'refused':
            try:
                envoyer_refus_inscription(c)
            except Exception:
                pass
    elif action == 'notify':
        c.notifie = True
        c.save()
    else:
        return JsonResponse({'error': 'Action inconnue'}, status=400)

    LABELS = {'pending': 'En attente', 'waiting': 'Mise en attente',
              'accepted': 'Acceptée', 'refused': 'Refusée'}
    c.refresh_from_db()
    return JsonResponse({
        'success': True,
        'statut': c.statut,
        'label': LABELS.get(c.statut, c.statut),
        'has_pdf': bool(c.pdf_inscription),
        'pdf_voir_url': f'/admin-cfld/candidature/{c.pk}/pdf/voir/' if c.pdf_inscription else None,
        'pdf_dl_url': f'/admin-cfld/candidature/{c.pk}/pdf/telecharger/' if c.pdf_inscription else None,
    })


@staff_required
def candidature_pdf_telecharger(request, pk):
    c = get_object_or_404(Candidature, pk=pk)
    if not c.pdf_inscription:
        raise Http404('PDF non disponible')
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(c.pdf_inscription))
    if not os.path.exists(pdf_path):
        raise Http404('Fichier PDF introuvable')
    return FileResponse(
        open(pdf_path, 'rb'),
        as_attachment=True,
        filename=f'inscription_{c.reference}.pdf',
        content_type='application/pdf',
    )


@staff_required
def candidature_pdf_voir(request, pk):
    c = get_object_or_404(Candidature, pk=pk)
    if not c.pdf_inscription:
        raise Http404('PDF non disponible')
    pdf_path = os.path.join(settings.MEDIA_ROOT, str(c.pdf_inscription))
    if not os.path.exists(pdf_path):
        raise Http404('Fichier PDF introuvable')
    return FileResponse(
        open(pdf_path, 'rb'),
        as_attachment=False,
        filename=f'inscription_{c.reference}.pdf',
        content_type='application/pdf',
    )


@staff_required
def candidature_pdf_regenerer(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    c = get_object_or_404(Candidature, pk=pk)
    try:
        generer_pdf_inscription(c)
        return JsonResponse({'success': True, 'message': 'PDF régénéré avec succès'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
