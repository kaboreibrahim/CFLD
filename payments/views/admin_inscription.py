from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from audit.utils import log_view
from payments.forms import PaiementInscriptionForm
from payments.models import PaiementInscription
from payments.services import calculer_echeances
from payments.pdf_utils import generer_recu_inscription

from .admin_utils import base_ctx, comptes_json, staff_required


@staff_required
def admin_paiements_inscription(request):
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', 'all')
    qs = PaiementInscription.objects.select_related('candidature', 'compte_paiement', 'valide_par')

    if q:
        qs = qs.filter(
            Q(candidature__nom__icontains=q)
            | Q(candidature__prenom__icontains=q)
            | Q(candidature__reference__icontains=q)
        )
    if statut != 'all':
        qs = qs.filter(statut_validation=statut)

    log_view(request, "PaiementInscription", "Consultation de la liste des paiements inscription.")
    ctx = base_ctx(request, 'paiements_inscription')
    ctx.update({
        'paiements': qs,
        'total': PaiementInscription.objects.count(),
        'nb_pending': PaiementInscription.objects.filter(statut_validation='pending').count(),
        'nb_approved': PaiementInscription.objects.filter(statut_validation='approved').count(),
        'nb_rejected': PaiementInscription.objects.filter(statut_validation='rejected').count(),
        'q': q,
        'statut_actif': statut,
    })
    return render(request, 'admin_cfld/paiements_inscription.html', ctx)


@staff_required
def admin_paiement_inscription_form(request, pk=None):
    obj = get_object_or_404(PaiementInscription, pk=pk) if pk else None
    form = PaiementInscriptionForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        paiement = form.save(commit=False)
        paiement.enregistre_par = request.user
        paiement.save()
        messages.success(request, "Paiement inscription enregistré.")
        return redirect('admin_paiements_inscription')
    ctx = base_ctx(request, 'paiements_inscription')
    ctx.update({'form': form, 'obj': obj, 'comptes_json': comptes_json()})
    return render(request, 'admin_cfld/paiement_inscription_form.html', ctx)


@staff_required
def admin_paiement_inscription_action(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requis'}, status=405)
    paiement = get_object_or_404(PaiementInscription, pk=pk)
    action = request.POST.get('action')

    if action == 'approve':
        paiement.statut_validation = 'approved'
        paiement.valide_par = request.user
        paiement.date_validation = timezone.now()
        paiement.save()
        return JsonResponse({'ok': True, 'statut': 'approved'})
    elif action == 'reject':
        paiement.statut_validation = 'rejected'
        paiement.valide_par = None
        paiement.date_validation = None
        paiement.save()
        return JsonResponse({'ok': True, 'statut': 'rejected'})
    elif action == 'delete':
        paiement.delete()
        return JsonResponse({'ok': True, 'deleted': True})

    return JsonResponse({'error': 'Action inconnue'}, status=400)


@staff_required
def admin_inscription_detail(request, pk):
    from payments.models import VersementCotisation
    paiement = get_object_or_404(
        PaiementInscription.objects.select_related(
            'candidature', 'compte_paiement', 'valide_par'
        ).prefetch_related('versement_cotisation'),
        pk=pk,
    )
    versement_auto = VersementCotisation.objects.filter(
        source_inscription=paiement
    ).select_related('cotisation', 'cotisation__joueur').first()

    plan = None
    if versement_auto:
        plan = calculer_echeances(versement_auto.cotisation)

    log_view(request, "PaiementInscription",
             f"Consultation du detail du paiement inscription {paiement}.", paiement.pk)
    ctx = base_ctx(request, "paiements_inscription")
    ctx.update({
        "paiement": paiement,
        "versement_auto": versement_auto,
        "plan": plan,
    })
    return render(request, "admin_cfld/inscription_detail.html", ctx)


@staff_required
def admin_inscription_pdf(request, pk):
    from django.http import HttpResponse
    from audit.utils import log_download
    paiement = get_object_or_404(PaiementInscription, pk=pk, statut_validation="approved")
    log_download(request, "PaiementInscription",
                 f"Telechargement du recu inscription {paiement}.", paiement.pk)
    buf = generer_recu_inscription(paiement)
    numero = paiement.candidature.reference
    response = HttpResponse(buf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=recu_inscription_{numero}.pdf'
    return response
